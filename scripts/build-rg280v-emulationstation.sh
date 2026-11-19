#!/bin/bash
# Build the original JZ4770 EmulationStation fork with private image/curl libraries.
set -euo pipefail
cd "$(dirname "$0")/.."
work="$PWD/output/rg280v-emulationstation"
mkdir -p "$work" work/dl/boost
if [ ! -d "$work/source/.git" ]; then git clone https://github.com/lualiliu/emulationstation-on-jz4770.git "$work/source"; fi
if [ ! -d "$work/distribution/.git" ]; then git clone https://github.com/ManuelSch81/RG350-EmulationStation_configured.git "$work/distribution"; fi
[ "$(git -C "$work/source" rev-parse HEAD)" = 3ab83b15b7bf033bd1a02c9e307b4fc4219107b7 ] || git -C "$work/source" checkout 3ab83b15b7bf033bd1a02c9e307b4fc4219107b7
[ "$(git -C "$work/distribution" rev-parse HEAD)" = 3c8f0473e539ae7a36e8dd5e39180dcdc33cf0f8 ] || git -C "$work/distribution" checkout 3c8f0473e539ae7a36e8dd5e39180dcdc33cf0f8
patch="$PWD/patches/rg280v-emulationstation.patch"
if ! git -C "$work/source" apply --reverse --check "$patch" 2>/dev/null; then git -C "$work/source" apply "$patch"; fi
# The historical JFrog URL redirects to an account-reactivation page.
if [ ! -s work/dl/boost/boost_1_83_0.tar.bz2 ]; then
 curl -fL --retry 2 https://archives.boost.io/release/1.83.0/source/boost_1_83_0.tar.bz2 -o work/dl/boost/boost_1_83_0.tar.bz2
fi
docker run --rm --platform linux/arm64 -i -v "$PWD:/workspace" \
 -v plumos-jz47xx-rg280v-build:/workspace/output/rg280v -w /workspace \
 plumos-jz47xx-build:bookworm bash -s <<'BUILD'
set -eu
t=/workspace/output/rg280v/host
w=/workspace/output/rg280v-emulationstation
export PATH="$t/bin:$PATH"
s=$t/mipsel-gcw0-linux-uclibc/sysroot
cp /workspace/output/rg280v/.config "$w/buildroot-config-before-build"
restore_config() { cp "$w/buildroot-config-before-build" /workspace/output/rg280v/.config; }
trap restore_config EXIT
work/buildroot/utils/config --file output/rg280v/.config --enable BR2_PACKAGE_BOOST --enable BR2_PACKAGE_BOOST_SYSTEM --enable BR2_PACKAGE_BOOST_FILESYSTEM --enable BR2_PACKAGE_BOOST_DATE_TIME --enable BR2_PACKAGE_EIGEN --enable BR2_PACKAGE_LIBCURL
make -C work/buildroot O=/workspace/output/rg280v BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace olddefconfig
make -C work/buildroot O=/workspace/output/rg280v BR2_EXTERNAL=/workspace/work/buildroot/board/opendingux:/workspace BR2_DL_DIR=/workspace/work/dl -j8 boost eigen libcurl
cmake -S "$w/source" -B "$w/build" \
 -DCMAKE_SYSTEM_NAME=Linux -DCMAKE_SYSTEM_PROCESSOR=mipsel \
 -DCMAKE_C_COMPILER=$t/bin/mipsel-gcw0-linux-uclibc-gcc \
 -DCMAKE_CXX_COMPILER=$t/bin/mipsel-gcw0-linux-uclibc-g++ \
 -DCMAKE_FIND_ROOT_PATH=$s -DCMAKE_FIND_ROOT_PATH_MODE_LIBRARY=ONLY -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY \
 -DCMAKE_FIND_ROOT_PATH_MODE_PACKAGE=ONLY -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER \
 -DCMAKE_CXX_FLAGS="-O2 -I$s/usr/include/eigen3 -I$s/usr/include/SDL2" -DBoost_NO_BOOST_CMAKE=ON
cmake --build "$w/build" -j8
mkdir -p "$w/runtime/lib" "$w/image-objects"
cp "$w/source/emulationstation" "$w/runtime/"
"$t/bin/mipsel-gcw0-linux-uclibc-strip" "$w/runtime/emulationstation"
cp -a "$s/usr/lib/"libcurl.so* "$w/runtime/lib/"
# The installed system SDL2_image has PNG only; do not replace it globally.
img=/workspace/output/rg280v/build/sdl2_image-2.6.3
for src in "$img"/IMG*.c; do
 "$t/bin/mipsel-gcw0-linux-uclibc-gcc" -O2 -fPIC -DLOAD_PNG -DLOAD_JPG -DLOAD_BMP -DLOAD_GIF -DLOAD_XPM -DLOAD_SVG -I"$img" -I"$s/usr/include/SDL2" -c "$src" -o "$w/image-objects/$(basename "$src" .c).o"
done
"$t/bin/mipsel-gcw0-linux-uclibc-gcc" -shared -Wl,-soname,libSDL2_image-2.0.so.0 -o "$w/runtime/lib/libSDL2_image-2.0.so.0" "$w"/image-objects/*.o -lSDL2 -lpng -ljpeg -lz
cp -L "$s/usr/lib/libjpeg.so.8" "$w/runtime/lib/"
cp "$img/LICENSE.txt" "$w/runtime/SDL_image-LICENSE.txt"
cp /workspace/output/rg280v/build/libcurl-8.4.0/COPYING "$w/runtime/curl-COPYING"
for license in /workspace/output/rg280v/build/*jpeg*/LICENSE.md; do
 if [ -f "$license" ]; then cp "$license" "$w/runtime/jpeg-LICENSE.md"; fi
done
cp "$w/source/LICENSE.md" "$w/source/CREDITS.md" "$w/source/opensans_license.txt" "$w/runtime/"
"$t/bin/mipsel-gcw0-linux-uclibc-readelf" -A "$w/runtime/emulationstation" | grep 'Soft float'
BUILD
bash scripts/build-rg280v-emulationstation-mesa.sh

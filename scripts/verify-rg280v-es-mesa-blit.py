#!/usr/bin/env python3
"""Run the actual Mesa tiled-copy function against guarded memory (native CPU)."""
import pathlib,resource,signal,subprocess,sys,tempfile
root=pathlib.Path(__file__).resolve().parents[1]
source=pathlib.Path(sys.argv[1]).read_text()
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
header=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>
#define ETNA_LAYOUT_TILED 1
#define DRM_ETNA_PREP_READ 1
#define DRM_ETNA_PREP_WRITE 2
struct pipe_box { int x,y,z,width,height,depth; };
struct pipe_blit_info { struct { int format; struct pipe_box box; } src; };
struct etna_resource { int layout; struct { int nr_samples; } base; void *bo; };
struct etna_resource_level { unsigned stride; };
static unsigned util_format_get_blocksize(int format) { return format; }
static void *etna_bo_map(void *bo) { return bo; }
static void etna_bo_cpu_prep(void *bo,int flags) {}
static void etna_bo_cpu_fini(void *bo) {}
'''
tail=r'''
static unsigned char *guarded(size_t size) {
    size_t page=sysconf(_SC_PAGESIZE), span=(size+page-1)/page*page;
    unsigned char *p=mmap(NULL,span+page*2,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
    assert(p!=MAP_FAILED); assert(!mprotect(p+page,span,PROT_READ|PROT_WRITE));
    return p+page+span-size;
}
int main(void) {
    for (int bytes=1; bytes<=4; bytes*=4) {
        for (int partial=0;partial<2;++partial) {
            int width=partial?63:64,height=64;
            size_t count=width*height*bytes;
            unsigned char *src=guarded(count),*dst=guarded(count);
            for(size_t n=0;n<count;++n)src[n]=(unsigned char)(n*17+3);
            memset(dst,0xA5,count);
            struct etna_resource s={ETNA_LAYOUT_TILED,{0},src},d={ETNA_LAYOUT_TILED,{0},dst};
            struct etna_resource_level level={width*bytes};
            struct pipe_blit_info blit={.src={.format=bytes,.box={.width=width,.height=height}}};
            bool ok=etna_manual_blit(&d,&level,0,&s,&level,0,&blit);
            if(partial){assert(!ok);for(size_t n=0;n<count;++n)assert(dst[n]==0xA5);}
            else{assert(ok);assert(!memcmp(src,dst,count));}
        }
    }
    return 0;
}
'''
def function(text):
    end=text.index('\nstatic inline',text.index('etna_manual_blit('))
    start=text.rfind('static bool',0,text.index('etna_manual_blit('))
    return text[start:end]
with tempfile.TemporaryDirectory(prefix='es-mesa-blit-') as temp:
    temp=pathlib.Path(temp)
    target=temp/'src/gallium/drivers/etnaviv/etnaviv_rs.c'
    target.parent.mkdir(parents=True);target.write_text(source)
    subprocess.run(['patch','-s','-d',str(temp),'-p1','-i',str(root/'patches/rg280v-emulationstation-mesa-tile-blit.patch')],check=True)
    patched=target.read_text()
    for label,text in [('original',source),('patched',patched)]:
        c=temp/(label+'.c');exe=temp/label
        c.write_text(header+function(text)+tail)
        subprocess.run(['cc','-O2',str(c),'-o',str(exe)],check=True)
        result=subprocess.run([str(exe)],capture_output=True)
        if label=='original':assert result.returncode==-signal.SIGSEGV,(label,result.returncode,result.stderr)
        else:assert result.returncode==0,(label,result.returncode,result.stderr)
        print(label,'exit',result.returncode)
print('PASS: original overruns guarded memory; patched R8/RGBA copies match and partial tiles fall back')

/* plumOS RG280V file picker for the GCW Zero FFPlay port. */
#include <SDL.h>
#include <SDL_ttf.h>
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <sys/stat.h>

#define WIDTH 320
#define HEIGHT 240
#define MAX_ITEMS 512
#define PATH_CAP 1024

struct item {
    char name[256];
    int directory;
};

static struct item items[MAX_ITEMS];
static int item_count;
static int selected;
static char current[PATH_CAP];
static SDL_Surface *video;
static SDL_Surface *canvas;
static TTF_Font *font;

static int is_media(const char *name)
{
    static const char *exts[] = {
        ".mp4", ".m4v", ".avi", ".mkv", ".mov", ".webm", ".ogv",
        ".mpeg", ".mpg", ".flv", ".mp3", ".m4a", ".ogg", ".flac",
        ".wav", ".aac", NULL
    };
    size_t len = strlen(name);
    int i;
    for (i = 0; exts[i]; ++i) {
        size_t n = strlen(exts[i]);
        if (len >= n && !strcasecmp(name + len - n, exts[i]))
            return 1;
    }
    return 0;
}

static int compare_items(const void *a, const void *b)
{
    const struct item *left = a;
    const struct item *right = b;
    if (left->directory != right->directory)
        return right->directory - left->directory;
    return strcasecmp(left->name, right->name);
}

static void list_dir(void)
{
    DIR *dir;
    struct dirent *entry;
    char path[PATH_CAP];
    struct stat st;
    item_count = 0;
    selected = 0;
    if (!current[0]) {
        strcpy(items[0].name, "SD1  /media/user");
        items[0].directory = 1;
        strcpy(items[1].name, "SD2  /media/data/sd2");
        items[1].directory = 1;
        item_count = 2;
        return;
    }
    dir = opendir(current);
    if (!dir) return;
    while ((entry = readdir(dir)) && item_count < MAX_ITEMS) {
        if (entry->d_name[0] == '.') continue;
        if (snprintf(path, sizeof(path), "%s/%s", current, entry->d_name)
            >= (int)sizeof(path)) continue;
        if (stat(path, &st)) continue;
        if (!S_ISDIR(st.st_mode) && (!S_ISREG(st.st_mode) || !is_media(entry->d_name)))
            continue;
        snprintf(items[item_count].name, sizeof(items[item_count].name), "%s", entry->d_name);
        items[item_count].directory = S_ISDIR(st.st_mode);
        ++item_count;
    }
    closedir(dir);
    qsort(items, item_count, sizeof(items[0]), compare_items);
}

static void draw_line(const char *text, int x, int y, SDL_Color color)
{
    SDL_Surface *glyph = TTF_RenderUTF8_Blended(font, text, color);
    SDL_Rect dest = {x, y, 0, 0};
    if (!glyph) return;
    SDL_BlitSurface(glyph, NULL, canvas, &dest);
    SDL_FreeSurface(glyph);
}

static void redraw(void)
{
    SDL_Rect rect;
    SDL_Color white = {235, 240, 237, 0};
    SDL_Color yellow = {255, 214, 91, 0};
    SDL_Color gray = {131, 153, 160, 0};
    int first = selected > 8 ? selected - 8 : 0;
    int i;
    SDL_FillRect(canvas, NULL, SDL_MapRGB(canvas->format, 5, 11, 14));
    draw_line("FFPlay  /  Select media", 8, 5, yellow);
    draw_line(current[0] ? current : "Choose SD card", 8, 27, gray);
    rect.x = 0; rect.y = 48; rect.w = WIDTH; rect.h = 1;
    SDL_FillRect(canvas, &rect, SDL_MapRGB(canvas->format, 48, 92, 102));
    for (i = first; i < item_count && i < first + 9; ++i) {
        char label[300];
        int row = i - first;
        if (i == selected) {
            rect.x = 5; rect.y = 55 + row * 19; rect.w = 310; rect.h = 19;
            SDL_FillRect(canvas, &rect, SDL_MapRGB(canvas->format, 35, 66, 65));
        }
        snprintf(label, sizeof(label), "%c %s", items[i].directory ? '/' : ' ', items[i].name);
        draw_line(label, 8, 55 + row * 19, i == selected ? yellow : white);
    }
    draw_line("A Open  B Back  SELECT Exit", 8, 225, gray);
    SDL_SoftStretch(canvas, NULL, video, NULL);
    SDL_Flip(video);
}

static void back(void)
{
    char *slash;
    if (!current[0]) return;
    if (!strcmp(current, "/media/user") || !strcmp(current, "/media/data/sd2")) {
        current[0] = 0;
    } else {
        slash = strrchr(current, '/');
        if (slash) *slash = 0;
    }
    list_dir();
}

int main(void)
{
    SDL_Event event;
    int done = 0;
    int chosen = 0;
    char result[PATH_CAP] = "";
    if (SDL_Init(SDL_INIT_VIDEO) || TTF_Init()) return 1;
    video = SDL_SetVideoMode(WIDTH, HEIGHT * 2, 16, SDL_SWSURFACE);
    if (!video) return 1;
    canvas = SDL_CreateRGBSurface(SDL_SWSURFACE, WIDTH, HEIGHT, 16,
                                  video->format->Rmask, video->format->Gmask,
                                  video->format->Bmask, video->format->Amask);
    font = TTF_OpenFont("/opk/default.otf", 14);
    if (!canvas || !font) return 1;
    list_dir();
    redraw();
    while (!done && SDL_WaitEvent(&event)) {
        char next[PATH_CAP];
        if (event.type == SDL_QUIT) break;
        if (event.type != SDL_KEYDOWN) continue;
        switch (event.key.keysym.sym) {
        case SDLK_ESCAPE:
            done = 1;
            break;
        case SDLK_LALT:
        case SDLK_BACKSPACE:
            back();
            break;
        case SDLK_UP:
            if (selected > 0) --selected;
            break;
        case SDLK_DOWN:
            if (selected + 1 < item_count) ++selected;
            break;
        case SDLK_LCTRL:
        case SDLK_RETURN:
            if (!item_count) break;
            if (!current[0]) {
                snprintf(current, sizeof(current), "%s",
                         selected ? "/media/data/sd2" : "/media/user");
                list_dir();
            } else if (snprintf(next, sizeof(next), "%s/%s", current,
                                items[selected].name) < (int)sizeof(next)) {
                if (items[selected].directory) {
                    snprintf(current, sizeof(current), "%s", next);
                    list_dir();
                } else {
                    snprintf(result, sizeof(result), "%s", next);
                    chosen = done = 1;
                }
            }
            break;
        default:
            break;
        }
        if (!done) redraw();
    }
    TTF_CloseFont(font);
    SDL_FreeSurface(canvas);
    SDL_Quit();
    if (chosen) puts(result);
    return chosen ? 0 : 1;
}

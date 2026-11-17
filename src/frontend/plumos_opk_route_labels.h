/* Names shared by the controller and text frontend. */
#ifndef PLUMOS_OPK_ROUTE_LABELS_H
#define PLUMOS_OPK_ROUTE_LABELS_H
static const char *plumos_opk_route_label(const char *id)
{
    if (strcmp(id, "atari800") == 0) return "Atari800";
    if (strcmp(id, "fba44") == 0) return "FBA44";
    if (strcmp(id, "temper") == 0) return "Temper";
    if (strcmp(id, "fceux223") == 0) return "FCEUX 2.2.3";
    if (strcmp(id, "genesisgx") == 0) return "Genesis Plus GX";
    if (strcmp(id, "pokemini") == 0) return "PokeMini";
    if (strcmp(id, "race") == 0) return "Race Explorer";
    if (strcmp(id, "crocods") == 0) return "CrocoDS";
    if (strcmp(id, "gambatte2020") == 0) return "Gambatte 2020";
    if (strcmp(id, "ohboy") == 0) return "OhBoy";
    if (strcmp(id, "stella") == 0) return "Stella";
    if (strcmp(id, "neo4all") == 0) return "NEO4ALL";
    if (strcmp(id, "handy") == 0) return "Handy";
    if (strcmp(id, "oswan") == 0) return "Oswan";
    if (strcmp(id, "smsplusgg") == 0) return "SMS Plus GG";
    if (strcmp(id, "smsplusms") == 0) return "SMS Plus MS";
    if (strcmp(id, "unrealspeccy") == 0) return "Unreal Speccy";
    if (strcmp(id, "gngeo") == 0) return "GnGeo";
    if (strcmp(id, "uae4all") == 0) return "UAE4All";
    return NULL;
}
#endif

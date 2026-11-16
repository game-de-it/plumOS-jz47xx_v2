#ifndef PLUMOS_RG280V_NO_SHAKE_H
#define PLUMOS_RG280V_NO_SHAKE_H

/* RG280V has no rumble motor. Keep the GCW Zero input tester source intact. */
typedef struct { int unused; } Shake_Device;
typedef struct {
  struct {
    struct {
      int waveform;
      int period;
      int magnitude;
      struct {
        int attackLength;
        int attackLevel;
        int fadeLength;
        int fadeLevel;
      } envelope;
    } periodic;
  } u;
  int direction;
  int length;
  int delay;
} Shake_Effect;

#define SHAKE_EFFECT_PERIODIC 0
#define SHAKE_PERIODIC_SINE 0
static inline int Shake_Init(void) { return 0; }
static inline int Shake_NumOfDevices(void) { return 0; }
static inline Shake_Device *Shake_Open(int index) { (void)index; return 0; }
static inline void Shake_InitEffect(Shake_Effect *effect, int type) {
  (void)effect; (void)type;
}
static inline int Shake_UploadEffect(Shake_Device *device, Shake_Effect *effect) {
  (void)device; (void)effect; return -1;
}
static inline int Shake_Play(Shake_Device *device, int id) {
  (void)device; (void)id; return -1;
}
static inline int Shake_Stop(Shake_Device *device, int id) {
  (void)device; (void)id; return -1;
}
static inline int Shake_EraseEffect(Shake_Device *device, int id) {
  (void)device; (void)id; return 0;
}
static inline int Shake_Close(Shake_Device *device) { (void)device; return 0; }
#endif

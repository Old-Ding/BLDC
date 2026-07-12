#ifndef BLDC_SIX_STEP_H
#define BLDC_SIX_STEP_H

typedef struct {
    int a;
    int b;
    int c;
} BldcPhaseCommand;

BldcPhaseCommand bldc_six_step_command(unsigned int step, int direction);

#endif

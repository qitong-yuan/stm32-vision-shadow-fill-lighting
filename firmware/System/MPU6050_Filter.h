#ifndef __MPU6050_FILTER_H
#define __MPU6050_FILTER_H

#include "stm32f10x.h"

// 滤波器类型选择
#define USE_LOW_PASS_FILTER  1  // 1:使用一阶低通滤波  0:使用滑动平均滤波

// 一阶低通滤波参数 (0-1之间，越小越平滑但响应越慢)
#define ALPHA 0.3f

// 滑动平均滤波参数
#define FILTER_SIZE 10

// MPU6050滤波数据结构
typedef struct {
    int16_t AX;
    int16_t AY;
    int16_t AZ;
    int16_t GX;
    int16_t GY;
    int16_t GZ;
} MPU6050_FilterData;

// 函数声明
void MPU6050_Filter_Init(void);
void MPU6050_Filter_Update(int16_t AX_Raw, int16_t AY_Raw, int16_t AZ_Raw, 
                           int16_t GX_Raw, int16_t GY_Raw, int16_t GZ_Raw);
void MPU6050_Filter_GetData(MPU6050_FilterData *data);
void MPU6050_Filter_SetBaseline(int16_t AX, int16_t AY, int16_t AZ,
                                int16_t GX, int16_t GY, int16_t GZ);
void MPU6050_Filter_GetRealData(MPU6050_FilterData *data);

#endif

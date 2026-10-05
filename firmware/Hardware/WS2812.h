#ifndef __WS2812_H
#define __WS2812_H

#include "AllHeader.h"

#define WS2812_LED_NUM      15      //三条灯带共15颗
#define WS2812_ZONE_SIZE     5      //每条灯带颗

//分区索引
#define ZONE_LEFT_START      0
#define ZONE_MID_START       5
#define ZONE_RIGHT_START    10

//WS2812 编码电平
#define SIG_1   0xF8    //11111000  高占空比 ~62.5%
#define SIG_0   0xE0    //11100000  低占空比 ~37.5%

//默认补光颜色
#define LIGHT_R     200
#define LIGHT_G     200
#define LIGHT_B     200

uint32_t ws281x_color(uint8_t, uint8_t, uint8_t);

void ws2812_GPIO_Init(void);
void ws2812_SPI_Init(void);
void ws2812_DMA_Init(void);
void ws2812_Init(void);
void ws2812_Send_Data(void);
void ws2812_AllShutOff(void);
void ws2812_Zone_On(uint8_t zone_start, uint8_t r, uint8_t g, uint8_t b);
void ws2812_Zone_Off(uint8_t zone_start);
void ws2812_Zone_Set(uint8_t zone_start, uint8_t percent);
void ws2812_Left_On(void);//左
void ws2812_Left_Off(void);
void ws2812_Mid_On(void);//中
void ws2812_Mid_Off(void) ; 
void ws2812_Right_On(void);//右
void ws2812_Right_Off(void);
#endif

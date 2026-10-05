#include "AllHeader.h"

uint8_t ws2812_data_buffer[WS2812_LED_NUM][24];

// GPIO&SPI&DMA 初始化，与上学期完全一致，不动
void ws2812_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStructure;
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA, ENABLE);
    GPIO_InitStructure.GPIO_Pin   = GPIO_Pin_7;
    GPIO_InitStructure.GPIO_Mode  = GPIO_Mode_AF_PP;
    GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
    GPIO_Init(GPIOA, &GPIO_InitStructure);
}

void ws2812_SPI_Init(void)
{
    SPI_InitTypeDef SPI_InitStructure;
    RCC_APB2PeriphClockCmd(RCC_APB2Periph_SPI1, ENABLE);
    SPI_InitStructure.SPI_Direction         = SPI_Direction_1Line_Tx;
    SPI_InitStructure.SPI_Mode              = SPI_Mode_Master;
    SPI_InitStructure.SPI_DataSize          = SPI_DataSize_8b;
    SPI_InitStructure.SPI_CPOL              = SPI_CPOL_Low;
    SPI_InitStructure.SPI_CPHA              = SPI_CPHA_2Edge;
    SPI_InitStructure.SPI_NSS               = SPI_NSS_Soft;
    SPI_InitStructure.SPI_BaudRatePrescaler = SPI_BaudRatePrescaler_8;
    SPI_InitStructure.SPI_FirstBit          = SPI_FirstBit_MSB;
    SPI_InitStructure.SPI_CRCPolynomial     = 7;
    SPI_Init(SPI1, &SPI_InitStructure);
    SPI_Cmd(SPI1, ENABLE);
    SPI_I2S_DMACmd(SPI1, SPI_I2S_DMAReq_Tx, ENABLE);
}

void ws2812_DMA_Init(void)
{
    DMA_InitTypeDef DMA_InitStructure;
    RCC_AHBPeriphClockCmd(RCC_AHBPeriph_DMA1, ENABLE);
    DMA_DeInit(DMA1_Channel3);
    DMA_InitStructure.DMA_PeripheralBaseAddr = (uint32_t)&(SPI1->DR);
    DMA_InitStructure.DMA_MemoryBaseAddr     = (uint32_t)ws2812_data_buffer;
    DMA_InitStructure.DMA_DIR                = DMA_DIR_PeripheralDST;
    DMA_InitStructure.DMA_BufferSize         = WS2812_LED_NUM * 24;
    DMA_InitStructure.DMA_PeripheralInc      = DMA_PeripheralInc_Disable;
    DMA_InitStructure.DMA_MemoryInc          = DMA_MemoryInc_Enable;
    DMA_InitStructure.DMA_PeripheralDataSize = DMA_PeripheralDataSize_Byte;
    DMA_InitStructure.DMA_MemoryDataSize     = DMA_MemoryDataSize_Byte;
    DMA_InitStructure.DMA_Mode               = DMA_Mode_Normal;
    DMA_InitStructure.DMA_Priority           = DMA_Priority_Medium;
    DMA_InitStructure.DMA_M2M                = DMA_M2M_Disable;
    DMA_Init(DMA1_Channel3, &DMA_InitStructure);
}

void ws2812_Init(void)
{
    ws2812_GPIO_Init();
    ws2812_SPI_Init();
    ws2812_DMA_Init();
    ws2812_AllShutOff();
    Delay_ms(WS2812_LED_NUM * 10);
}


//刷新和组色
void ws2812_Send_Data(void)
{
    DMA_Cmd(DMA1_Channel3, DISABLE);
    DMA_ClearFlag(DMA1_FLAG_TC3);
    DMA_SetCurrDataCounter(DMA1_Channel3, 24 * WS2812_LED_NUM);
    DMA_Cmd(DMA1_Channel3, ENABLE);
}


uint32_t ws281x_color(uint8_t red, uint8_t green, uint8_t blue)
{
    return (uint32_t)green << 16 | (uint32_t)red << 8 | blue;
}


//全灭
void ws2812_AllShutOff(void)
{
    uint16_t i;
    uint8_t j;
    for (i = 0; i < WS2812_LED_NUM; i++)
        for (j = 0; j < 24; j++)
            ws2812_data_buffer[i][j] = SIG_0;
    ws2812_Send_Data();
    Delay_ms(10 * WS2812_LED_NUM);
}

//本学期新增
//点亮指定区域
void ws2812_Zone_On(uint8_t zone_start, uint8_t r, uint8_t g, uint8_t b)
{
    uint8_t i, j;
    uint32_t color = ws281x_color(r, g, b);
    for (j = zone_start; j < zone_start + WS2812_ZONE_SIZE; j++) {
        for (i = 0; i < 24; i++) {
            ws2812_data_buffer[j][i] = (((color << i) & 0x800000) ? SIG_1 : SIG_0);
        }
    }
    ws2812_Send_Data();
    Delay_ms(10);
}

//熄灭指定区域
void ws2812_Zone_Off(uint8_t zone_start)
{
    uint8_t i, j;
    for (j = zone_start; j < zone_start + WS2812_ZONE_SIZE; j++)
        for (i = 0; i < 24; i++)
            ws2812_data_buffer[j][i] = SIG_0;
    ws2812_Send_Data();
    Delay_ms(10);
}

//按百分比点亮指定区域 0=灭，100最亮
void ws2812_Zone_Set(uint8_t zone_start, uint8_t percent)
{
    uint8_t i, j;
    uint8_t r, g, b;
    uint32_t color;

    if (percent > 100) percent = 100;

    r = (uint8_t)((uint16_t)LIGHT_R * percent / 100);//颜色按LIGHT_R/G/B，亮度乘以percent/100
    g = (uint8_t)((uint16_t)LIGHT_G * percent / 100);
    b = (uint8_t)((uint16_t)LIGHT_B * percent / 100);

    color = ws281x_color(r, g, b);
    for (j = zone_start; j < zone_start + WS2812_ZONE_SIZE; j++) {
        for (i = 0; i < 24; i++) {
            ws2812_data_buffer[j][i] = (((color << i) & 0x800000) ? SIG_1 : SIG_0);
        }
    }
    ws2812_Send_Data();
    Delay_ms(10);
}


//快捷接口

void ws2812_Left_On(void)  { ws2812_Zone_On(ZONE_LEFT_START,  LIGHT_R, LIGHT_G, LIGHT_B); }//左
void ws2812_Left_Off(void) { ws2812_Zone_Off(ZONE_LEFT_START); }

void ws2812_Mid_On(void)   { ws2812_Zone_On(ZONE_MID_START,   LIGHT_R, LIGHT_G, LIGHT_B); }//中
void ws2812_Mid_Off(void)  { ws2812_Zone_Off(ZONE_MID_START); }

void ws2812_Right_On(void)  { ws2812_Zone_On(ZONE_RIGHT_START, LIGHT_R, LIGHT_G, LIGHT_B); }//右
void ws2812_Right_Off(void) { ws2812_Zone_Off(ZONE_RIGHT_START); }

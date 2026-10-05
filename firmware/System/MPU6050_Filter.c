#include "MPU6050_Filter.h"

// 滤波后的数据
static MPU6050_FilterData filtered_data = {0};

// 基准值（用于计算相对变化）
static MPU6050_FilterData baseline_data = {0};

#if USE_LOW_PASS_FILTER
    // 一阶低通滤波的上一次值
    static float AX_last = 0, AY_last = 0, AZ_last = 0;
    static float GX_last = 0, GY_last = 0, GZ_last = 0;
    static uint8_t first_run = 1;
#else
    // 滑动平均滤波缓冲区
    static int16_t AX_Buffer[FILTER_SIZE] = {0};
    static int16_t AY_Buffer[FILTER_SIZE] = {0};
    static int16_t AZ_Buffer[FILTER_SIZE] = {0};
    static int16_t GX_Buffer[FILTER_SIZE] = {0};
    static int16_t GY_Buffer[FILTER_SIZE] = {0};
    static int16_t GZ_Buffer[FILTER_SIZE] = {0};
    static uint8_t filter_index = 0;
#endif

/**
 * @brief  滤波器初始化
 * @param  无
 * @retval 无
 */
void MPU6050_Filter_Init(void)
{
    filtered_data.AX = 0;
    filtered_data.AY = 0;
    filtered_data.AZ = 0;
    filtered_data.GX = 0;
    filtered_data.GY = 0;
    filtered_data.GZ = 0;
    
    baseline_data.AX = 0;
    baseline_data.AY = 0;
    baseline_data.AZ = 0;
    baseline_data.GX = 0;
    baseline_data.GY = 0;
    baseline_data.GZ = 0;
    
#if USE_LOW_PASS_FILTER
    first_run = 1;
#else
    filter_index = 0;
    for(uint8_t i = 0; i < FILTER_SIZE; i++)
    {
        AX_Buffer[i] = 0;
        AY_Buffer[i] = 0;
        AZ_Buffer[i] = 0;
        GX_Buffer[i] = 0;
        GY_Buffer[i] = 0;
        GZ_Buffer[i] = 0;
    }
#endif
}

#if USE_LOW_PASS_FILTER
/**
 * @brief  一阶低通滤波
 * @param  new_value: 新采样值
 * @param  last_value: 上次滤波结果的指针
 * @retval 滤波后的值
 */
static int16_t Low_Pass_Filter(int16_t new_value, float *last_value)
{
    float filtered = ALPHA * new_value + (1.0f - ALPHA) * (*last_value);
    *last_value = filtered;
    return (int16_t)filtered;
}
#else
/**
 * @brief  滑动平均滤波
 * @param  buffer: 滤波缓冲区
 * @param  new_value: 新采样值
 * @retval 滤波后的值
 */
static int16_t Moving_Average_Filter(int16_t *buffer, int16_t new_value)
{
    int32_t sum = 0;
    buffer[filter_index] = new_value;
    
    for(uint8_t i = 0; i < FILTER_SIZE; i++)
    {
        sum += buffer[i];
    }
    
    return (int16_t)(sum / FILTER_SIZE);
}
#endif

/**
 * @brief  更新滤波数据
 * @param  AX_Raw, AY_Raw, AZ_Raw: 加速度原始数据
 * @param  GX_Raw, GY_Raw, GZ_Raw: 陀螺仪原始数据
 * @retval 无
 */
void MPU6050_Filter_Update(int16_t AX_Raw, int16_t AY_Raw, int16_t AZ_Raw, 
                           int16_t GX_Raw, int16_t GY_Raw, int16_t GZ_Raw)
{
#if USE_LOW_PASS_FILTER
    // 第一次运行直接赋值
    if(first_run)
    {
        AX_last = AX_Raw;
        AY_last = AY_Raw;
        AZ_last = AZ_Raw;
        GX_last = GX_Raw;
        GY_last = GY_Raw;
        GZ_last = GZ_Raw;
        first_run = 0;
    }
    
    // 一阶低通滤波
    filtered_data.AX = Low_Pass_Filter(AX_Raw, &AX_last);
    filtered_data.AY = Low_Pass_Filter(AY_Raw, &AY_last);
    filtered_data.AZ = Low_Pass_Filter(AZ_Raw, &AZ_last);
    filtered_data.GX = Low_Pass_Filter(GX_Raw, &GX_last);
    filtered_data.GY = Low_Pass_Filter(GY_Raw, &GY_last);
    filtered_data.GZ = Low_Pass_Filter(GZ_Raw, &GZ_last);
#else
    // 滑动平均滤波
    filtered_data.AX = Moving_Average_Filter(AX_Buffer, AX_Raw);
    filtered_data.AY = Moving_Average_Filter(AY_Buffer, AY_Raw);
    filtered_data.AZ = Moving_Average_Filter(AZ_Buffer, AZ_Raw);
    filtered_data.GX = Moving_Average_Filter(GX_Buffer, GX_Raw);
    filtered_data.GY = Moving_Average_Filter(GY_Buffer, GY_Raw);
    filtered_data.GZ = Moving_Average_Filter(GZ_Buffer, GZ_Raw);
    
    // 更新循环索引
    filter_index = (filter_index + 1) % FILTER_SIZE;
#endif
}

/**
 * @brief  获取滤波后的数据
 * @param  data: 数据结构指针
 * @retval 无
 */
void MPU6050_Filter_GetData(MPU6050_FilterData *data)
{
    data->AX = filtered_data.AX;
    data->AY = filtered_data.AY;
    data->AZ = filtered_data.AZ;
    data->GX = filtered_data.GX;
    data->GY = filtered_data.GY;
    data->GZ = filtered_data.GZ;
}

/**
 * @brief  设置基准值（用于校准）
 * @param  AX, AY, AZ: 加速度基准值
 * @param  GX, GY, GZ: 陀螺仪基准值
 * @retval 无
 */
void MPU6050_Filter_SetBaseline(int16_t AX, int16_t AY, int16_t AZ,
                                int16_t GX, int16_t GY, int16_t GZ)
{
    baseline_data.AX = AX;
    baseline_data.AY = AY;
    baseline_data.AZ = AZ;
    baseline_data.GX = GX;
    baseline_data.GY = GY;
    baseline_data.GZ = GZ;
}

/**
 * @brief  获取相对于基准值的实际数据
 * @param  data: 数据结构指针
 * @retval 无
 */
void MPU6050_Filter_GetRealData(MPU6050_FilterData *data)
{
    data->AX = filtered_data.AX - baseline_data.AX;
    data->AY = filtered_data.AY - baseline_data.AY;
    data->AZ = filtered_data.AZ - baseline_data.AZ;
    data->GX = filtered_data.GX - baseline_data.GX;
    data->GY = filtered_data.GY - baseline_data.GY;
    data->GZ = filtered_data.GZ - baseline_data.GZ;
}

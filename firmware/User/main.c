#include "AllHeader.h"
#include "Serial.h"
#include "OLED.h"
#include "WS2812.h"

char    uart_rx_buffer[64];
uint8_t uart_rx_index = 0;
uint8_t uart_cmd_ready = 0;

//灯带区域状态（用于 OLED 显示） 
static uint8_t state_left  = 0;
static uint8_t state_mid   = 0;
static uint8_t state_right = 0;

static void OLED_ShowLightState(void)
{
    //第3行显示当前三路灯状态 
    OLED_ShowString(3, 1, "L:");
    OLED_ShowString(3, 3, state_left  ? "ON " : "OFF");
    OLED_ShowString(3, 7, "M:");
    OLED_ShowString(3, 9, state_mid   ? "ON " : "OFF");
    OLED_ShowString(4, 1, "R:");
    OLED_ShowString(4, 3, state_right ? "ON " : "OFF");
}

static void Process_Command(char *cmd)
{
    //cmd 指向 '#' 开头的字符串
    if (cmd[0] != '#') return;

    if (strncmp(cmd + 1, "LEFT*", 5) == 0)//第一类
    {
        ws2812_Left_On();
        state_left = 1;
        Serial_SendString("ACK:LEFT_ON\r\n");
    }
    else if (strncmp(cmd + 1, "MID*", 4) == 0)
    {
        ws2812_Mid_On();
        state_mid = 1;
        Serial_SendString("ACK:MID_ON\r\n");
    }
    else if (strncmp(cmd + 1, "RIGHT*", 6) == 0)
    {
        ws2812_Right_On();
        state_right = 1;
        Serial_SendString("ACK:RIGHT_ON\r\n");
    }
    else if (strncmp(cmd + 1, "ALL*", 4) == 0)
    {
        ws2812_Left_On();
        ws2812_Mid_On();
        ws2812_Right_On();
        state_left = state_mid = state_right = 1;
        Serial_SendString("ACK:ALL_ON\r\n");
    }
    else if (strncmp(cmd + 1, "OFF*", 4) == 0)
    {
        ws2812_AllShutOff();
        state_left = state_mid = state_right = 0;
        Serial_SendString("ACK:ALL_OFF\r\n");
    }
    else if (strncmp(cmd + 1, "LEFTON*", 7) == 0)
    {
        ws2812_Left_On();
        state_left = 1;
        Serial_SendString("ACK:LEFT_ON\r\n");
    }
    else if (strncmp(cmd + 1, "LEFTOFF*", 8) == 0)
    {
        ws2812_Left_Off();
        state_left = 0;
        Serial_SendString("ACK:LEFT_OFF\r\n");
    }
    else if (strncmp(cmd + 1, "MIDON*", 6) == 0)
    {
        ws2812_Mid_On();
        state_mid = 1;
        Serial_SendString("ACK:MID_ON\r\n");
    }
    else if (strncmp(cmd + 1, "MIDOFF*", 7) == 0)
    {
        ws2812_Mid_Off();
        state_mid = 0;
        Serial_SendString("ACK:MID_OFF\r\n");
    }
    else if (strncmp(cmd + 1, "RIGHTON*", 8) == 0)
    {
        ws2812_Right_On();
        state_right = 1;
        Serial_SendString("ACK:RIGHT_ON\r\n");
    }
    else if (strncmp(cmd + 1, "RIGHTOFF*", 9) == 0)
    {
        ws2812_Right_Off();
        state_right = 0;
        Serial_SendString("ACK:RIGHT_OFF\r\n");
    }
    else if ((cmd[1]=='L' || cmd[1]=='M' || cmd[1]=='R')//第二类
             && cmd[2]>='0' && cmd[2]<='9'
             && cmd[3]>='0' && cmd[3]<='9'
             && cmd[4]>='0' && cmd[4]<='9'
             && cmd[5]=='*')
    {
        uint8_t pct = (cmd[2]-'0')*100 + (cmd[3]-'0')*10 + (cmd[4]-'0');
        if (pct > 100) pct = 100;

        if (cmd[1]=='L') { ws2812_Zone_Set(ZONE_LEFT_START,  pct); state_left  = (pct>0); }
        if (cmd[1]=='M') { ws2812_Zone_Set(ZONE_MID_START,   pct); state_mid   = (pct>0); }
        if (cmd[1]=='R') { ws2812_Zone_Set(ZONE_RIGHT_START, pct); state_right = (pct>0); }

        Serial_SendString("ACK:");
        Serial_SendByte(cmd[1]);
        Serial_SendByte(cmd[2]);
        Serial_SendByte(cmd[3]);
        Serial_SendByte(cmd[4]);
        Serial_SendString("\r\n");
    }

    else
    {
        Serial_SendString("ERR:UNKNOWN_CMD\r\n");
    }

    OLED_ShowLightState();//刷新OLED上状态显示
}


int main(void)
{
    Serial_Init();//115200
    OLED_Init();
    ws2812_Init(); 


    OLED_ShowString(1, 1, "SmartLight V2");//开机动画
    OLED_ShowString(2, 1, "Wait command..");
    OLED_ShowString(3, 1, "L:OFF M:OFF");
    OLED_ShowString(4, 1, "R:OFF");

    Serial_SendString("READY\r\n");//通知已经就绪

    while (1)
    {
        if (uart_cmd_ready)//有完整命令的时候就解析
        {
            uart_cmd_ready = 0;
            Process_Command(uart_rx_buffer);
        }
    }
}

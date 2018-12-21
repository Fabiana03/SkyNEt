'<ADbasic Header, Headerversion 001.001>
' Process_Number                 = 1
' Initial_Processdelay           = 1000
' Eventsource                    = Timer
' Control_long_Delays_for_Stop   = No
' Priority                       = High
' Version                        = 1
' ADbasic_Version                = 5.0.8
' Optimize                       = Yes
' Optimize_Level                 = 1
' Info_Last_Save                 = DARWIN-PC  Darwin-PC\PNPNteam
'<Header End>
#Include ADwinGoldII.inc
DIM DATA_1[40003] AS LONG AS FIFO  
DIM DATA_2[40003] AS LONG AS FIFO
DIM DATA_3[40003] AS LONG AS FIFO
DIM DATA_4[40003] AS LONG AS FIFO
DIM DATA_5[40003] AS LONG AS FIFO
DIM DATA_6[40003] AS LONG AS FIFO
DIM DATA_7[40003] AS LONG AS FIFO
DIM DATA_8[40003] AS LONG AS FIFO
DIM DATA_9[40003] AS LONG AS FIFO
DIM DATA_10[40003] AS LONG AS FIFO
DIM DATA_11[40003] AS LONG AS FIFO
DIM DATA_12[40003] AS LONG AS FIFO
DIM counter AS LONG

INIT:
  FIFO_Clear(1)
  FIFO_Clear(2)
  FIFO_Clear(3)
  FIFO_Clear(4)
  FIFO_Clear(5)
  FIFO_Clear(6)
  FIFO_Clear(7)
  FIFO_Clear(8)
  FIFO_Clear(9)
  FIFO_Clear(10)
  FIFO_Clear(11)
  FIFO_Clear(12)
  
  Rem set continuous conversion and range [-5, 5]V for ADCs
  Seq_Mode(2, 2)
  Seq_Set_Gain(2, 0)
  Seq_Mode(4, 2)
  Seq_Set_Gain(4, 0)
  Seq_Mode(6, 2)
  Seq_Set_Gain(6, 0)
  Seq_Mode(8, 2)
  Seq_Set_Gain(8, 0)
  Seq_Mode(10, 2)
  Seq_Set_Gain(10, 0)
  Seq_Mode(12, 2)
  Seq_Set_Gain(12, 0)
  Seq_Mode(14, 2)
  Seq_Set_Gain(14, 0)
  Seq_Mode(16, 2)
  Seq_Set_Gain(16, 0)
  
  Seq_Select(1010101010101010b) Rem selects even ADCs (look in ADwin Gold II manual)
  Seq_Start(1010101010101010b)
  Rem Seq_Select(0FFFFh)
  Rem Seq_Start(10b)
  
  Rem write parameters
  Par_1 = 0
  Par_2 = 0
  Par_3 = 0
  Par_4 = 0
  
  Rem start flag
  Par_80 = 0
  
  Rem Amount of data to write
  Par_79 = 0
  Rem counter 
  counter = -1  
  
  
EVENT:
  If (Par_80 = 1) Then
    If (counter < Par_79) Then
      If (counter < Par_79 - 1) Then
        Rem writing
        Par_1 = DATA_1
        DAC(1, Par_1)
        Par_2 = DATA_2
        DAC(2, Par_2)
        Par_3 = DATA_3
        DAC(3, Par_3)
        Par_4 = DATA_4
        DAC(4, Par_4)
      EndIf
    
      Rem reading
      DATA_5 = Seq_Read(2) 
      DATA_6 = Seq_Read(4) 
      DATA_7 = Seq_Read(6) 
      DATA_8 = Seq_Read(8) 
      DATA_9 = Seq_Read(10) 
      DATA_10 = Seq_Read(12) 
      DATA_11 = Seq_Read(14) 
      DATA_12 = Seq_Read(16)
   
      Inc(counter)
    EndIf
  EndIf

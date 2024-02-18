# Echo characters over serial (requires a USB to UART cable)

include ../bronzebeard/definitions/FE310-G002.asm

CLOCK_FREQ = 16000000
BAUD_RATE  = 115200

# jump to "main" since programs execute top to bottom
# we do this to enable writing helper funcs at the top
j main


# Func: serial_init
# Arg: a0 = baud rate
serial_init:
    # enable IOF0 for pins 16 (UART0_RX) and 17 (UART0_TX)
    li t0, GPIO_BASE_ADDR
    li t1, (1 << 17) | (1 << 16)
    sw t1, GPIO_IOF_EN_OFFSET(t0)

    # calculate and store clkdiv
    li t0, UART_BASE_ADDR_0
    li t1, CLOCK_FREQ
    div t1, t1, a0
    sw t1, UART_DIV_OFFSET(t0)

    # enable transmit
    li t0, UART_BASE_ADDR_0
    li t1, UART_TXCTRL_TXEN
    sw t1, UART_TXCTRL_OFFSET(t0)

    # enable receive
    li t0, UART_BASE_ADDR_0
    li t1, UART_RXCTRL_RXEN
    sw t1, UART_RXCTRL_OFFSET(t0)

serial_init_done:
    ret


# Func: serial_getc
# Ret: a0 = character received
serial_getc:
    li t0, UART_BASE_ADDR_0        # load UART base addr into t0
serial_getc_loop:
    lw a0, UART_RXDATA_OFFSET(t0)  # load data into a0
    addi t1, zero, 1               # setup empty bit
    slli t1, t1, 31                # ...
    and t1, a0, t1                 # isolate empty bit
    bnez t1, serial_getc_loop      # keep looping until ready to recv
    andi a0, a0, 0xff              # isolate bottom 8 bits
serial_getc_done:
    ret


# Func: serial_putc
# Arg: a0 = character to send
serial_putc:
    li t0, UART_BASE_ADDR_0       # load UART base addr into t0
serial_putc_loop:
    lw t1, UART_TXDATA_OFFSET(t0)  # load data into t1
    addi t2, zero, 1               # setup full bit
    slli t2, t2, 31                # ...
    and t2, t1, t2                 # isolate full bit
    bnez t2, serial_putc_loop      # keep looping until ready to send
    andi a0, a0, 0xff              # isolate bottom 8 bits
    sw a0, UART_TXDATA_OFFSET(t0)  # write char from a0
serial_putc_done:
    ret


# UART Pins
# (based on schematic)
# --------------------
# RX: GPIO Pin 16
# TX: GPIO Pin 17

main:
    li a0, BAUD_RATE
    call serial_init

# main loop (read a char, write a char, repeat)
loop:
    call serial_getc
    call serial_putc
    j loop

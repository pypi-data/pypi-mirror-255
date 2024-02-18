# Echo characters over serial (requires a USB to UART cable)

include ../bronzebeard/definitions/GD32VF103.asm

CLOCK_FREQ = 8000000  # default GD32BF103 clock freq
USART_BAUD = 115200   # desired USART baud rate


# jump to "main" since programs execute top to bottom
# we do this to enable writing helper funcs at the top
j main


# Func: rcu_init
# Arg: a0 = RCU base addr
# Arg: a1 = RCU config
# Ret: none
rcu_init:
    # store config
    sw a1, RCU_APB2EN_OFFSET(a0)
rcu_init_done:
    ret


# Func: gpio_init
# Arg: a0 = GPIO port base addr
# Arg: a1 = GPIO pin number
# Arg: a2 = GPIO config (4 bits)
# Ret: none
gpio_init:
    # advance to CTL0
    addi t0, a0, GPIO_CTL0_OFFSET

    # if pin number is less than 8, CTL0 is correct
    slti t1, a1, 8
    bnez t1, gpio_init_config

    # else we need CTL1 and then subtract 8 from the pin number
    addi t0, t0, 4
    addi a1, a1, -8

gpio_init_config:
    # multiply pin number by 4 to get shift amount
    slli a1, a1, 2

    # load current config
    lw t1, 0(t0)

    # align and clear existing pin config
    li t2, 0b1111
    sll t2, t2, a1
    not t2, t2
    and t1, t1, t2

    # align and apply new pin config
    sll a2, a2, a1
    or t1, t1, a2

    # store updated config
    sw t1, 0(t0)

gpio_init_done:
    ret


# Func: usart_init
# Arg: a0 = USART base addr
# Arg: a1 = USART clkdiv
# Ret: none
usart_init:
    # store clkdiv
    sw a1, USART_BAUD_OFFSET(a0)
    # enable USART (enable RX, enable TX, enable USART)
    li t0, USART_CTL0_UEN | USART_CTL0_TEN | USART_CTL0_REN
    sw t0, USART_CTL0_OFFSET(a0)
usart_init_done:
    ret


# Func: getc
# Arg: a0 = USART base addr
# Ret: a1 = character received (a1 here for simpler getc + putc loops)
getc:
    lw t0, USART_STAT_OFFSET(a0)  # load status into t0
    andi t0, t0, USART_STAT_RBNE  # isolate read buffer not empty (RBNE) bit
    beqz t0, getc                 # keep looping until ready to recv
    lw a1, USART_DATA_OFFSET(a0)  # load char into a1
getc_done:
    ret


# Func: putc
# Arg: a0 = USART base addr
# Arg: a1 = character to send
# Ret: none
putc:
    lw t0, USART_STAT_OFFSET(a0)  # load status into t0
    andi t0, t0, USART_STAT_TBE   # isolate transmit buffer empty (TBE) bit
    beqz t0, putc                 # keep looping until ready to send
    sw a1, USART_DATA_OFFSET(a0)  # write char from a1
putc_done:
    ret


main:
    # enable RCU (AFIO, GPIO port A, and USART0)
    li a0, RCU_BASE_ADDR
    li a1, RCU_APB2EN_USART0EN | RCU_APB2EN_PAEN | RCU_APB2EN_AFEN
    call rcu_init

    # enable TX pin
    li a0, GPIO_BASE_ADDR_A
    li a1, 9
    li a2, GPIO_CONFIG_AF_PP_50MHZ
    call gpio_init

    # enable RX pin
    li a0, GPIO_BASE_ADDR_A
    li a1, 10
    li a2, GPIO_CONFIG_IN_FLOAT
    call gpio_init

    # enable USART0
    li a0, USART_BASE_ADDR_0
    li a1, CLOCK_FREQ // USART_BAUD
    call usart_init

# main loop (read a char, write a char, repeat)
loop_init:
    # setup USART base addr (won't change in getc + putc loop)
    li a0, USART_BASE_ADDR_0
loop:
    call getc
    call putc
    j loop

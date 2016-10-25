twoway (scatter s t if t > 0, msize(vtiny)), by (onboard engage)
separate s, by (onboard)
separate s1, by (engage)
separate s2, by (engage)
sum s11 s12 s21 s22 if t > 0
inequal7 s11 s12 s21 s22 if t > 0
separate nc, by (onboard)
separate nc1, by (engage)
separate nc2, by (engage)
sum nc11 nc12 nc21 nc22 if t > 0
inequal7 nc11 nc12 nc21 nc22 if t > 0

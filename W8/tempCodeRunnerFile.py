x1, x2 = comb_pos_list[0][0], comb_pos_list[1][0]
    y1, y2 = comb_pos_list[0][1], comb_pos_list[1][1]
    r1, r2 = anchor1_dis, anchor2_dis
    d = math.sqrt((x1-x2)**2 + (y1 - y2)**2)
    l = (r1**2 - r2**2 + d **2)
    h = math.sqrt(r1**2 - l**2)
    predicted_pos[0] = l/d * (x2-x1) + h/d(y2-y1) + x1
    predicted_pos[1] = l/d * (y2-y1) - h/d(x2 - x1) + y1
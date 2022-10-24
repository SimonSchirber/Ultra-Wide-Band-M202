
    # #######3rd Column#####
    # ###Anchor/Smart Device Positions
    # obj_text = small_font.render('Object', True, green)
    # x_text = small_font.render('X(m)', True, green)
    # y_text = small_font.render('Y(m)', True, green)
    # z_text = small_font.render('Z(m)', True, green)
    # xobj_text_dis = column3_xcord + round(width_column3*.35)
    # yobj_text_dis = column3_xcord + round(width_column3 * .57)
    # zobj_text_dis = column3_xcord + round(width_column3 * .79)
    # screen.blit(obj_text, (column3_xcord + space, space))
    # screen.blit(x_text, (xobj_text_dis, space)) 
    # screen.blit(y_text, (yobj_text_dis, space))
    # screen.blit(z_text, (zobj_text_dis, space))
    # #Write Details of positions in X,Y, Z boxes
    # for obj_num in range(len(comb_pos_list)):
    #     y_obj_dis = (1 + obj_num) * obj_space
    #     pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    #     x_data_text = small_font.render(str(comb_pos_list[obj_num][0]), True, green)
    #     y_data_text = small_font.render(str(comb_pos_list[obj_num][1]), True, green)
    #     z_data_text = small_font.render(str(comb_pos_list[obj_num][2]), True, green)
    #     name_data_text = smallest_font.render(comb_name_list[obj_num], True, green)
    #     screen.blit(name_data_text, (space + column3_xcord, space + y_obj_dis))
    #     screen.blit(x_data_text, (xobj_text_dis, space + y_obj_dis))
    #     screen.blit(y_data_text, (yobj_text_dis, space + y_obj_dis))
    #     screen.blit(z_data_text, (zobj_text_dis, space + y_obj_dis))   
    #     #Draw the bottom line and horizontal dividers
    #     if (obj_num ==  len(comb_pos_list) - 1):
    #         y_obj_dis = (2 + obj_num) * obj_space
    #         pygame.draw.line(screen, white, (column3_xcord, y_obj_dis), (width_display, y_obj_dis), 1)
    #         pygame.draw.line(screen, white, (xobj_text_dis-space, 0), (xobj_text_dis-space, y_obj_dis), 1)
    #         pygame.draw.line(screen, white, (yobj_text_dis- space, 0), (yobj_text_dis-space, y_obj_dis), 1)
    #         pygame.draw.line(screen, white, (zobj_text_dis- space, 0), (zobj_text_dis-space, y_obj_dis), 1)
from bifacialvf import simulate




def threading_helper(lower_bound, upper_bound):
    writefiletitle = "bifacialvf/data/Output/_" + str(lower_bound)

    while lower_bound != upper_bound:
        simulate("bifacialvf/data/724010TYA.csv", writefiletitle, 10, lower_bound, 1, 1.5, "interior",
                 0.013 , 6, "glass", "glass", 0.62, False, True, )
        lower_bound = lower_bound+1




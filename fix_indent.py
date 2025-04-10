with open('systems/synapstex.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

with open('systems/synapstex.py', 'w', encoding='utf-8') as f:
    for i, line in enumerate(lines, 1):
        if i == 554:
            f.write('            else:\n                # Use screen space for UI particles\n')
        elif i == 555:
            f.write('                spawn_x = x if x is not None else random.uniform(0, self.screen_width)\n')
        elif i == 556:
            f.write('                spawn_y = y if y is not None else random.uniform(0, self.screen_height)\n')
        else:
            f.write(line)

print("Fixed indentation in systems/synapstex.py") 
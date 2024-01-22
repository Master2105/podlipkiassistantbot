#  if message.text.lower() == "отменить":
#         cell_list = sh.sheet1.range(f'A{next_row}:L{next_row}')
#         # Заполняем все ячейки.
#         for cell in cell_list:
#             cell.value = ''
#         # Обновляем заполненные данные.
#         sh.sheet1.update_cells(cell_list)
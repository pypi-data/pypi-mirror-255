from PIL import Image
from tqdm import tqdm
import pytesseract
import pandas as pd
# import easyocr
from PyPDF2 import PdfFileReader, PdfFileWriter, PdfMerger, PageObject
from pdf2image import convert_from_path
import img2pdf


from multiprocessing import Process, Manager, Lock, Pool
from concurrent.futures import ThreadPoolExecutor

import os
import json
import re
import shutil


import threading
from queue import Queue
import itertools



class Archivarius():

    def get_text_easyocr(self, image_path, delete_file = False) -> str:
        '''
        Извлекаем текст с помощью Easyocr
        
        Args:
            :image_path (str): полный путь до jpg файла
            
            :delete_file (bool): удаление файла после извлечения текста

        Return: text (str): извлеченный текст с изображения 

        '''
        import easyocr

        reader = easyocr.Reader(['ru'])
        result = reader.readtext(image_path, detail = 0)

        text = ''.join(result)
        result = text.lower()
        result = result.replace('\n', ' ')
        
        if delete_file == True:
            os.remove(image_path)
        
        return text

    def get_text(
            self, image_path, delete_file = False, 
            path_tes = r'M:\Analytics\a.shulegin\job\liberty\t\tesseract.exe',
            ) -> str:


        '''Извлекаем текст с помощью Tesseract

        Args:
            - image_path (str): полный путь до jpg файла
            
            - delete_file (bool): удаление файла после извлечения текста

            - path_tes (str): Полный путь до установленного Тисеракта

        Return:
  
            text (str): извлеченный текст с изображения 

            '''

        if not os.path.isfile(path_tes):
            raise Exception ('Не указан путь до тисеракта в переменную path_tes')


        pytesseract.pytesseract.tesseract_cmd = path_tes
        Image.MAX_IMAGE_PIXELS = 9999218750

        text = pytesseract.image_to_string(image_path, lang='rus')
        text = text.lower()
        text = text.replace('\n', ' ')

        if delete_file == True:
            os.remove(image_path)

        return text

    def tiff_or_png_to_jpg(self, file, path) -> None:
        '''Конвертирует PNG-файл в JPG-файл
        
        Args:
            
            file (str): название файла 

            path (str): путь где лежит файл

        Return: None

            Сохраняет файл в тойже дериктории 
   
        '''
        try:
            # Замените 'input.tif' и 'output.jpg' на соответствующие имена ваших файлов
            input_tif = path + '\\' + file
            output_jpg = path + '\\' + file[:-4] + '.jpg'

            # Открываем TIFF-изображение
            with Image.open(input_tif) as img:
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Конвертируем и сохраняем его в формате JPEG
                img.save(output_jpg, 'JPEG')
        except Exception as exc:
            print(exc)
            pass

    def jpeg_to_jpg(self, file, path) -> None:
        '''Конвертирует JPEG-файл в JPG-файл
        
        Args:
            
            file (str): название файла 

            path (str): путь где лежит файл

        Return: None

            Сохраняет файл в тойже дериктории 

        '''
        new_filename = os.path.join(path, file.replace(".jpeg", ".jpg"))
        os.rename(os.path.join(path, file), new_filename)

    def jpg_to_pdf(self, file, path) -> None:
        '''Конвертирует JPG-файл в PDF-файл
        
        Args:
            
            file (str): название файла 

            path (str): путь где лежит файл

        Return: None

            Сохраняет файл в тойже дериктории 

        '''
        
        image_paths = os.path.join(path, file)
        pdf_path = os.path.join(path, file.replace(".jpg", ".pdf"))

        with open(pdf_path, "wb") as f:
                    f.write(img2pdf.convert(image_paths, rotation=img2pdf.Rotation.ifvalid))

class PDF_Toolbox():
    ''' 
    Класс для работы с пдф файлами

    Metods :
        two_in_one_list_pdf_soft : Создает файл pdf 2 листа на одном в новой директории.
        
        extract_text_from_pdf : Возращает текст из файла pdf.

        split_pdf : Разделяет по стронично PDF файл

        merge_pdfs : Объединяет два файла PDF в один

        f103 : Разделяет файл на 3 листа первая середина и последняя.

    '''
    list_func = {
        'params': ['параметр1'],
    }

    def two_in_one_list_pdf_soft(self, path, new_path) -> None:
        '''Создает файл pdf 2 листа на одном в новой директории

        Args:
            path (str): путь до файла.

            new_path (str): путь куда сохранить новый файл

        Return:
            Сохраняет файл по новому пути.
        
        '''

        # Проверка на пустой файл
        if os.path.getsize(path) == 0:
            print(f"Ошибка: Файл {path} пустой.")
            return

        reader = PdfFileReader(open(path, 'rb'), strict=False)
        writer = PdfFileWriter()
        num = 0
        pageNum = reader.numPages
        if pageNum > 1:
            while num < pageNum-1:
                min_page = reader.getPage(num)

                big_page = PageObject.createBlankPage(None, min_page.mediaBox.getWidth()*2, min_page.mediaBox.getHeight())
                #mergeScaledTranslatedPage(page2, scale, tx, ty, expand=False)
                big_page.mergeScaledTranslatedPage(reader.getPage(num), 1, 0, 0)
                if num + 1 < pageNum:
                    if reader.getPage(num + 1).mediaBox.getWidth() > 600:

                        big_page.mergeScaledTranslatedPage(reader.getPage(num + 1), 1, float(min_page.mediaBox.getWidth()), 0)
                        writer.addPage(big_page)
                    else:
                        big_page.mergeScaledTranslatedPage(reader.getPage(num + 1), 1, float(min_page.mediaBox.getWidth()), 0)
                        writer.addPage(big_page)
                num = num + 2
            if pageNum % 2 == 1:
                min_page = reader.getPage(num)
                big_page = PageObject.createBlankPage(None, min_page.mediaBox.getWidth() * 2, min_page.mediaBox.getHeight())
                big_page.mergeScaledTranslatedPage(reader.getPage(num), 1, 0, 0)
                writer.addPage(big_page)

            file_name = os.path.basename(path)
            new_path = os.path.join(new_path, file_name)

            with open(new_path[:-4] + '_2for1.pdf', 'wb') as f:
                writer.write(f)
        else:
            shutil.copy(path, new_path[:-4] + '_2for1.pdf')

    def extract_text_from_pdf(self, pdf_path:str) -> str:
        ''' 
        Возращает текст из файла pdf.
        
        Args:
            pdf_path (str): путь к pdf файлу.

        Return:
            text (str): текст из файла pdf.
        '''
        text = ""

        # Открывает pdf файл
        with open(pdf_path, 'rb') as file:
            pdf_reader = PdfFileReader(file)
            num_pages = pdf_reader.numPages

        # Получаем текст из всех страниц
            for page_num in range(num_pages):
                page = pdf_reader.getPage(page_num)
                text += page.extractText()

        # Возращаем текст
        return text

    def split_pdf(self, input_pdf_path, output_folder) -> None:
        '''Разделяет по стронично PDF файл
        
        Args:
            input_pdf_path (str): Файл pdf для разделения.

            output_folder (str): Путь к папке для сохранения.

        Return:
            Ничего

        '''

        # Открываем PDF-файл для чтения
        with open(input_pdf_path, 'rb') as pdf_file:
            # Создаем объект для работы с PDF
            pdf_reader = PdfFileReader(pdf_file)

            # Проходим по каждой странице и создаем отдельные PDF-файлы
            for page_num in range(pdf_reader.numPages):
                # Создаем новый объект для записи в новый файл
                pdf_writer = PdfFileWriter()

                # Получаем текущую страницу
                page = pdf_reader.getPage(page_num)

                # Добавляем страницу к новому файлу
                pdf_writer.addPage(page)

                # Создаем имя нового файла
                output_file_path = f"{output_folder}/page_{page_num + 1}.pdf"

                # Открываем новый файл для записи
                with open(output_file_path, 'wb') as output_pdf:
                    # Записываем страницу в новый файл
                    pdf_writer.write(output_pdf)

    def merge_pdfs(self, input_pdf1:str, input_pdf2:str, output_pdf:str) -> None:
        '''Объединяет два файла PDF в один

        Args:
            input_pdf1 (str): Путь до первого файла   

            input_pdf2 (str): Путь до второго файла

            output_pdf (str): Путь куда сохранить файл и его название

        Return:
            None
    
        '''

        merger = PdfMerger()

        # Добавляем первый PDF
        merger.append(input_pdf1)

        # Добавляем второй PDF
        merger.append(input_pdf2)

        # Сохраняем объединенный PDF
        merger.write(output_pdf)

        # Закрываем объединитель
        merger.close()

    def f103(self, input_path:str, output_path:str) -> None:
        '''Разделяет файл на 3 листа первая середина и последняя.
        
        Args:
            input_path (str): прямой путь к файлу;\n

            output_path (str): в какую папку сохранить файл.\n

        Return: None

            Сохраняет файл в новой папке

        '''
        file = input_path.split('\\')[-1]
        filename = file.split('.')[-2]

        try:
            with open(input_path, 'rb') as file:
                pdf_reader = PdfFileReader(file)
                
                if pdf_reader.numPages <= 0:
                    print("Ошибка: Пустой файл")
                    return

                for num in range(1, pdf_reader.numPages-1):
                    pdf_writer = PdfFileWriter()

                    page = pdf_reader.getPage(0)
                    pdf_writer.addPage(page)

                    page = pdf_reader.getPage(num)
                    pdf_writer.addPage(page)

                    page = pdf_reader.getPage(pdf_reader.numPages-1)
                    pdf_writer.addPage(page)

                    # Открываем файл для записи объединенного PDF
                    with open(f'{output_path}\{filename}_{num+1}.pdf', 'wb') as output_file:
                        # Записываем содержимое PdfFileWriter в выходной файл
                        pdf_writer.write(output_file)

                pdf_writer = PdfFileWriter()

                page = pdf_reader.getPage(0)
                pdf_writer.addPage(page)

                page = pdf_reader.getPage(pdf_reader.numPages-1)
                pdf_writer.addPage(page)

                # Открываем файл для записи объединенного PDF
                with open(f'{output_path}\{filename}_{1}.pdf', 'wb') as output_file:
                    # Записываем содержимое PdfFileWriter в выходной файл
                    pdf_writer.write(output_file)

            print(f"Успешно создан новый PDF-файл")

        except FileNotFoundError:
            print(f"Ошибка: Файл не найден: {input_path}")
        except PermissionError:
            print(f"Ошибка: Недостаточно прав для доступа к файлу: {input_path}")
        except Exception as e:
            print(f"Произошла ошибка: {e}")

    def pdf_to_jpg(self, file, path) -> None:
        '''Конвертирует pdf файл в jpg
        
            Args:
                file (str): название файла

                path (str): путь где лежит файл

            Returns: None

                Сохраняет картинку в той же папке
        '''
        try:
            # Конвертируем PDF в изображения
            images = convert_from_path(path + '\\' +  file, poppler_path=r'M:\Analytics\a.shulegin\job\liberty\poppler-23.08.0\Library\bin')

            # Перебираем каждую страницу и сохраняем ее как отдельное изображение
            for i, image in enumerate(images):
                output_file = f'{file[:-4]}_page_{i + 1}.jpg'  # Создаем уникальное имя для каждой страницы
                image.save(path + '\\' + output_file, 'JPEG')
        except Exception as exc:
            print(exc)
            pass


class Model_Tolboox(Archivarius, PDF_Toolbox):

    def convert_file(self, file, path) -> None:
        '''Конвертирует файл в jpg
        
        Сейчас потдерживает такие форматы как:

            - PNG

            - TIF

            - JPEG

        Args:

            file (str): название файла

            path (str): директория в которой он лежит

        Return: None

            Сохраняет файл в исходной директории 

        '''
        if 'pdf' in file:
            self.pdf_to_jpg(file, path)
        if 'png' in file or 'tif' in file:
            self.tiff_or_png_to_jpg(file, path)
        if '.jpeg' in file:
            self.jpeg_to_jpg(file, path)

    def get_text_in_image_pdf(self, path) -> None:
        '''Конвертирует все файлы в директории в JPG-файлы 
        и извлекает из них тектст, сохраняет в TXT-файл в формате:
        {'Полный путь': 'Текст из фотографии'}

        Args:
            
        path (str): путь до директории где лежат файлы

        Returns: None

            Сохраняет результат в result.txt

        '''

        print('[!] Конвертация файлов')
        for direct, folder, files in os.walk(path):
            for file in tqdm(files):
                self.convert_file(file, direct)
        print('[!] Конвертация файлов завершена')


        print('[!] Идет извлечение текста')
        for direct, folder, files in os.walk(path):
            for file in tqdm(files):
                if 'jpg' in file:
                    fullpath = os.path.join(direct, file)
                    text = self.get_text_ts(fullpath)
                    
                    with open('result.txt', 'a', encoding='utf-8') as f:
                        f.write(str({fullpath: text}))
                        f.write('\n')
        print('[!] Извлечение текста закончено')

    def get_text_in_pdf(self, path) -> str:
        '''Извлекает текст из PDF-файла и сохраняет в TXT-файл
        в формате: {'Полный путь': 'Текст из фотографии'}

        Args:
            
            path (str): путь до директории где лежат файлы

        Returns: None

            Сохраняет результат в result.txt

        '''


        print('[!] Идет извлечение текста')
        for direct, folder, files in os.walk(path):
            for file in tqdm(files):
                if 'pdf' in file:
                    fullpath = os.path.join(direct, file)
                    text = self.extract_text_from_pdf(fullpath)
                    
                    if text:
                        with open('result.txt', 'a', encoding='utf-8') as f:
                            f.write(str({fullpath: text}))
                            f.write('\n')
                    else:
                        print(f'У файла {fullpath} нет текста')

        print('[!] Извлечение текста закончено')

    def res_sorted(self, file:str, cl_class:str, cl_path:str) -> None:
        '''Открывает итоговый файл и сортирует файлы по классам
        
        В нем должено содержаться:

            - Колонка с полным путем до файла

            - Колонка с номером класса к которому относиться файл

        Args:

            - file (str): путь до Excel-файла

            - cl_class (str): Название колонки с классами

            - cl_path (str): Название колонки с полными путями к файлам

        Return: None

            - Создает в текущей дериктории папку promes_resulte_*name с классифицированными делами

        '''
        df = pd.read_excel(file)
        path_list = {}
        clases = {}
        name = file.split('\\')[-1]
        name = name.split('.')[0]
        for path, clas in tqdm(zip(df['path'], df['class_name'])):
            '''Сортеруем файлы по классу название папки = номер класса'''
            try:    
                file = path.split('\\')
                fio = file[-3].split('_')
                fio = fio[-1]
                
                folder_path = f'promes_resulte_{name}' + '\\' + fio + '\\' + str(clas)
                
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                
                shutil.copy2(path, folder_path + '\\' + file[-1])
                path_list[folder_path] = fio
                clases[folder_path] = clas
            except Exception as exc:
                passs


class Model_Tolboox_mult(Archivarius, PDF_Toolbox):
    '''
    Класс многопоточит методы классов Archivarius и  PDF_Toolbox.

    Список методов которые сейчас подлежат многопоточности
        - extract_text_from_pdf
        - merge_pdfs
        - get_text
        - get_text_easyocr
        - two_in_one_list_pdf_soft

    Основной метод это multfunc.
    Как его использовать:

        - В параметр, process_func необходимо передать название функции (str) которую 
    нужно замногопоточить;

        - В параметр, num_process прописываем количество потоком;

        - В параметр, params необходимо передать список [['параметр1'], ['параметр2'], ... ],
    МАКСИМУМ 3 параметра, ВАЖНО передавать параметры в таком же парядке в каком они указанны в функции,
    которую вы многопоточите.


    multfunc будет проходиться циклом по параметрама и передовать их в функцию обработки (process_func).

    Пример использования:

        model = Model_Tolboox_mult()
        path = r'M:\Документы БД\_2024 Прикрепление файлов клиентов\01.09 ГК_16 досье\ГК_16\приложение\приложение к договору уступки ФАЛКОН_ГЛ 30.11.2023'
        input_pdf2 = []
        input_pdf1 = []
        output_pdf = []

        for direct, folder, files in os.walk(path):
            for file1, file2 in zip(files[::2], files[1::2]):
                new_name = os.path.join(direct, file2)
                input_pdf2.append(os.path.join(direct, file2))
                input_pdf1.append(os.path.join(direct, file1))
                output_pdf.append(new_name + '1')

        model.multfunc(
            params = [input_pdf1, input_pdf2, output_pdf],
            process_func='merge_pdfs',
            num_process = 10,
                    )

    '''

    list_func = {
        'extract_text_from_pdf': PDF_Toolbox.extract_text_from_pdf,
        'merge_pdfs': PDF_Toolbox.merge_pdfs,
        'get_text': Archivarius.get_text,
        'get_text_easyocr': Archivarius.get_text_easyocr,
        'two_in_one_list_pdf_soft': PDF_Toolbox.two_in_one_list_pdf_soft, 
    }

    def __init__(self):
        self.result_queue = Manager().Queue()

    def process(self, args_list:list) -> None:
        '''
        Метод для обработки списка аргументов в нескольких потоках.

        :param args_list: Список аргументов, где каждый элемент - кортеж (process_func, *params).
        :return: None
        '''
        for args in [args_list]:
            process_func, *params = args
            result = Model_Tolboox_mult.list_func[process_func](self, *params)

        if result:
            self.result_queue.put({file: result})

    def write_to_file(self):
        '''
        Метод для записи результатов в файл.

        :return: None
        '''
        with open('result.txt', 'a', encoding='utf-8') as f:
            while not self.result_queue.empty():
                result = self.result_queue.get()
                f.write(str(result))
                f.write('\n')

    def multfunc(self, params:list, process_func:str, num_process:int) -> None:
        '''
        Метод для выполнения функции в нескольких потоках.

        :param params: Список параметров для передачи в функцию.
        :param process_func: Имя функции для выполнения в нескольких потоках.
        :param num_process: Количество потоков.
        :return: None
        '''
        args_list = []

        with tqdm(total=len(params)) as pbar:
            def update(*a):
                pbar.update()



        # Создаем пул процессов и отслеживаем прогресс; Pool(*), где *- это кол-во потоков
        with Pool(num_process) as pool:

            if len(params) == 3:
                for param1, param2, param3 in zip(params[0], params[1], params[2]):
                    args_list.append((process_func, param1, param2, param3))

            if len(params) == 2:
                for param1, param2 in zip(params[0], params[1]):
                    args_list.append((process_func, param1, param2))

            if len(params) == 1:
                for param1 in params[0]:
                    args_list.append((process_func, param1))

            for _ in pool.imap_unordered(
                    self.process, args_list):
                update()


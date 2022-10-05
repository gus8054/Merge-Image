from tkinter import *
from tkinter import filedialog, messagebox
from tkinter import ttk
from PIL import Image, ImageGrab
import os
import time
import keyboard

class App(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack()

        # 파일 프레임
        self.file_frame = Frame(self)
        self.file_frame.pack(fill="x", padx=10, pady=10)

        self.add_file_btn = Button(self.file_frame, text="파일 추가", command=self.add_file)
        self.add_file_btn.pack(side="left", ipadx=3, ipady=3)

        self.delete_file_btn = Button(self.file_frame, text="파일 삭제", command=self.delete_file)
        self.delete_file_btn.pack(side="right", ipadx=3, ipady=3)

        # 리스트 프레임
        self.listbox_frame = Frame(self)
        self.listbox_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.listbox_scrollbar = Scrollbar(self.listbox_frame, orient=VERTICAL)
        self.listbox_scrollbar.pack(side="right", fill='y')

        self.listbox = Listbox(self.listbox_frame, activestyle='none', height=15, selectmode=EXTENDED, yscrollcommand=self.listbox_scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)

        self.listbox_scrollbar['command'] = self.listbox.yview

        # 저장 경로 프레임
        self.save_dir_frame = LabelFrame(self, text="저장 경로")
        self.save_dir_frame.pack(fill="x", padx=10, pady=10)

        self.save_dir_entry = Entry(self.save_dir_frame, state="readonly", readonlybackground="#ffffff")
        self.save_dir_entry.pack(side='left', fill='x', expand=True, padx=10, pady=10, ipady=6)

        self.change_save_dir_btn = Button(self.save_dir_frame, text="저장 경로 변경", command=self.change_path)
        self.change_save_dir_btn.pack(side="right", ipadx=3, ipady=3, padx=10, pady=10)

        # 옵션 프레임
        self.option_frame = LabelFrame(self, text="옵션 설정")
        self.option_frame.pack(fill="x", padx=10, pady=10)

        self.width_label = Label(self.option_frame, text="가로 길이")
        self.width_label.pack(side="left", padx=10, pady=10)

        self.widths = ["원본 크기 유지", "1024", "640"]
        self.width_combobox = ttk.Combobox(self.option_frame, values=self.widths, state="readonly")
        self.width_combobox.current(0)
        self.width_combobox.pack(side="left", padx=10, pady=10)

        self.ext_label = Label(self.option_frame, text="확장자")
        self.ext_label.pack(side="left", padx=10, pady=10)

        self.exts = ["png", "jpg", "bmp"]
        self.ext_combobox = ttk.Combobox(self.option_frame, values=self.exts, state="readonly")
        self.ext_combobox.current(0)
        self.ext_combobox.pack(side="left", padx=10, pady=10)

        self.margin_label = Label(self.option_frame, text="이미지 사이 간격(px)")
        self.margin_label.pack(side="left", padx=10, pady=10)

        self.margins = ["0", "30", "60", "90"]
        self.margin_combobox = ttk.Combobox(self.option_frame, values=self.margins, state="readonly")
        self.margin_combobox.current(0)
        self.margin_combobox.pack(side="left", padx=10, pady=10)

        # 실행 프레임
        self.execute_frame = Frame(self)
        self.execute_frame.pack(side="right", fill='both', expand=True, padx=10, pady=10)

        self.execute_p_var = DoubleVar()
        self.execute_progressbar = ttk.Progressbar(self.execute_frame, maximum=100, mode="determinate", variable=self.execute_p_var) # indeterminate : 언제 끝날지 모름
        self.execute_progressbar.pack(side="top", fill="x", padx=10, pady=10)

        self.stop_btn = Button(self.execute_frame, text="중지", command=self.stop)
        self.stop_btn.pack(side="right", anchor="s", ipadx=20, ipady=3, padx=10, pady=10)

        self.run_btn = Button(self.execute_frame, text="변환", command=self.run)
        self.run_btn.pack(side="right", anchor="s", ipadx=20, ipady=3, padx=10, pady=10)

        # 스크린샷 프레임
        self.screenshot_frame = LabelFrame(self, text="스크린샷")
        self.screenshot_frame.pack(side="left", fill="both", padx=10, pady=10)

        self.screenshot_info_label = Label(self.screenshot_frame, text="캡처 버튼 : [F9]")
        self.screenshot_info_label.pack(side="left", padx=10, pady=10)
        
        self.screenshot_delay_label = Label(self.screenshot_frame, text="지연 시간")
        self.screenshot_delay_label.pack(side="left", padx=10, pady=10)

        self.screenshot_delay_time = ["지연 없음", "1초", "2초", "3초"]
        self.screenshot_delay_combobox = ttk.Combobox(self.screenshot_frame, values=self.screenshot_delay_time, state="readonly")
        self.screenshot_delay_combobox.current(0)
        self.screenshot_delay_combobox.pack(side="left", padx=10, pady=10)

        keyboard.add_hotkey("F9", self.screenshot) # 사용자가 F9 키를 누르면 스크린 샷 저장

    def add_file(self):
        res = filedialog.askopenfilenames(filetypes=(("PNG 파일", "*.png"), ("모든 파일", "*.*")))
        if res == "":
            return
        for filename in res:
            self.listbox.insert(END, filename)

    def delete_file(self):
        selected_idxs = self.listbox.curselection()
        for idx in reversed(selected_idxs):
            self.listbox.delete(idx)

    def change_path(self):
        res = filedialog.askdirectory()
        if res == "":
            return

        self.save_dir_entry['state'] = "normal"
        self.save_dir_entry.delete(0, END)
        self.save_dir_entry.insert(0, res)
        self.save_dir_entry['state'] = "readonly"

    def merge_img(self):
        # 옵션 가져오기
        option_width = self.width_combobox.get().strip()
        option_ext = self.ext_combobox.get().strip().lower()
        option_margin = int(self.margin_combobox.get().strip())

        # 이미지들을 한번에 처리할 images 리스트 생성
        images = [Image.open(x) for x in self.listbox.get(0, END)] 

        # 가로 길이 옵션을 처리한다. 
        # "원본 유지"가 아닌 "1024"와 같은 숫자형 문자열이라면 isdigit()이 True가 된다.
        # 단, 음수와 소수점이 들어간 실수는 False를 반환하지만 가로크기에 음수와 소수점형태의 실수는 오지않으니 상관없다.
        if option_width.isdigit(): 
            option_width = int(option_width)
            image_sizes = [(option_width, option_width * image.size[1] // image.size[0]) for image in images]
        else:
            image_sizes = [(image.size[0], image.size[1]) for image in images]

        # 이미지들의 가로길이 세로길이를 max(), sum() 함수를 사용하기 위해 시퀀스로 정리한다.
        widths, heights = zip(*image_sizes)
        max_width = max(widths)
        total_height = sum(heights) + (option_margin * (len(images) - 1))

        # 기본 베이스가 될 이미지를 새로 만든다. 이 이미지 위에 각 이미지들을 덮어씌우는 방식으로 진행한다.
        new_img = Image.new("RGB", (max_width, total_height), (255, 255, 255))

        # 기본 베이스위에 덮어쓸 이미지의 y좌표이다. 
        y_offset = 0
        
        for idx, image in enumerate(images):
            # 프로그래스바 조정
            self.execute_p_var.set((idx) / len(images) * 100)
            self.execute_progressbar.update()

            # 이미지 크기 조정
            image = image.resize(image_sizes[idx])

            # 이미지 덮어쓰기
            new_img.paste(image, (0, y_offset))
            y_offset += image.size[1] + option_margin
        else:
            # 프로그래스바 조정
            self.execute_p_var.set(100)
            self.execute_progressbar.update()
        
        filename = "text." + option_ext
        new_img.save(os.path.join(self.save_dir_entry.get(), filename))

    def run(self):
        if self.listbox.size() == 0:
            messagebox.showwarning(title="경고", message="파일을 추가하십시오.")
            return
        if self.save_dir_entry.get() == "":
            messagebox.showwarning(title="경고", message="저장경로를 설정하십시오.")
            return

        self.merge_img()
        
    def stop(self):
        self.master.destroy()

    def screenshot(self):
        # 저장경로 설정이 안되어있을 경우 경고 메시지
        if self.save_dir_entry.get() == "":
            messagebox.showwarning(title="경고", message="저장경로를 설정하십시오.")
            return
        # 지연 시간 옵션을 가져온다.
        delay_time = self.screenshot_delay_combobox.get().strip()

        # 값의 통일성을 위해 "지연 없음"을 "0초"로 변환한다.
        if delay_time == "지연 없음":
            delay_time = "0초"
    
        # "0초", "1초", "2초" 와 같은 문자열에서 뒤에 "초"만 제거해서 숫자형으로 만든후 타입을 정수로 변환한다..
        delay_time = int(delay_time[:-1])
    
        # time모듈을 사용하여 해당 시간(s)만큼 대기를 건다.
        time.sleep(delay_time)
        
        # 2020년 6월 1일 10시 20분 30초 -> _20200601_102030
        curr_time = time.strftime("_%Y%m%d_%H%M%S")
        filename = f"image{curr_time}.png"
        img = ImageGrab.grab()
        img.save(os.path.join(self.save_dir_entry.get(), filename))

root = Tk()
myapp = App(root)

myapp.master.resizable(False, False)
myapp.master.title("이미지 세로로 합치기")

myapp.mainloop()

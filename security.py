# the results folder has the saved images and the name of image is the hidden text on it.
from tkinter import *
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import numpy as np

class TextInImage:
    def __init__(self, window):
        self.window = window
        self.window.title("Hide Text In Image App")
        self.window.geometry("1000x650")
        self.window.configure(bg="#e6f2ff")  
        self.inimage = None
        self.text = ""
        self.res_image = None
        self.lsb_count = IntVar(value=1)
        self.creategui()
        
    def creategui(self):
        frcontrol = Frame(self.window, bg="#e6f2ff")
        frcontrol.pack(pady=15)
        load_btn = Button(frcontrol, text="Select Image", command=self.chooseimage, width=20,
                          bg="#008080", fg="white", font=("Arial", 12, "bold"), relief=FLAT)
        load_btn.pack(side=LEFT, padx=10)
        
        intext = Frame(self.window, bg="#e6f2ff")
        intext.pack(pady=10)
        Label(intext, text="Message to Hide:", bg="#e6f2ff", font=("Arial", 12)).pack()
        self.textarea = Text(intext, height=3, width=40, font=("Arial", 12), bg="#ffffff", wrap=WORD, bd=2, relief=SOLID)
        self.textarea.pack(pady=5)

        fr = Frame(self.window, bg="#e6f2ff")
        fr.pack(pady=10)

        Label(fr, text="Choose the number of Bits:", bg="#e6f2ff", font=("Arial", 12)).pack()
        Radiobutton(fr, text="1", variable=self.lsb_count, value=1, bg="#e6f2ff", font=("Arial", 12)).pack(side=LEFT, padx=5)
        Radiobutton(fr, text="2", variable=self.lsb_count, value=2, bg="#e6f2ff", font=("Arial", 12)).pack(side=LEFT, padx=5)
        Radiobutton(fr, text="3", variable=self.lsb_count, value=3, bg="#e6f2ff", font=("Arial", 12)).pack(side=LEFT, padx=5)
        
        controllers = Frame(self.window, bg="#e6f2ff")
        controllers.pack(pady=10)
        Button(controllers, text="Encode Message", command=self.hiding, width=20, bg="#3b5998", fg="white", font=("Arial", 12, "bold")).pack(side=LEFT, padx=10)
        Button(controllers, text="Decode Message", command=self.appearing, width=20, bg="#e74c3c", fg="white", font=("Arial", 12, "bold")).pack(side=LEFT, padx=10)
        Button(controllers, text="Save Encoded Image", command=self.save, width=20, bg="#9C27B0", fg="white", font=("Arial", 12, "bold")).pack(side=LEFT, padx=10)

        self.image_dis = Canvas(self.window, width=1000, height=320, bg="white")
        self.image_dis.pack(pady=20)

        self.cover_dis = None
        self.result_dis = None

    def chooseimage(self):
        file_path = filedialog.askopenfilename(filetypes=[("Bitmap Files", "*.bmp")])
        if file_path:
            self.inimage = Image.open(file_path)
            self.disimage(self.inimage, x_position=200, tag="original")

    def disimage(self, img, x_position, tag):
        imgresized = img.resize((450, 280), Image.LANCZOS)
        img_dis = ImageTk.PhotoImage(imgresized)
        self.image_dis.delete(tag) 
        self.image_dis.create_image(x_position, 160, anchor=CENTER, image=img_dis, tags=tag)

        if tag == "original":
            self.cover_dis = img_dis
        else:
            self.result_dis = img_dis

    def hiding(self):
        if not self.inimage:
            messagebox.showwarning("Warning", "Please select an image first.")
            return
        self.text = self.textarea.get("1.0", END).strip() + '\0'  
        if not self.text:
            messagebox.showwarning("Warning", "Please enter text to hide.")
            return
        img_array = np.array(self.inimage)
        imgf = img_array.flatten()
        text_in_binary = ''.join([format(ord(char), '08b') for char in self.text])
        bits_to_use = self.lsb_count.get()
        clearbits = 255 - ((1 << bits_to_use) - 1)
        index = 0
        for i in range(len(imgf)):
            if index >= len(text_in_binary):
                break
            imgf[i] = imgf[i] & clearbits
            bits_for_pixel = text_in_binary[index:index + bits_to_use]
            bits_for_pixel = bits_for_pixel + '0' * (bits_to_use - len(bits_for_pixel))
            imgf[i] |= int(bits_for_pixel, 2)
            index += bits_to_use
        res_array = imgf.reshape(img_array.shape)
        self.res_image = Image.fromarray(res_array.astype('uint8'), 'RGB')

        self.disimage(self.inimage, x_position=200, tag="original")
        self.disimage(self.res_image, x_position=700, tag="encoded")

    def appearing(self):
        if not self.inimage:
            messagebox.showwarning("Warning", "No image selected.")
            return
        
        
        decoded_message = self.decoding(self.inimage, self.lsb_count.get())
        if decoded_message:
            messagebox.showinfo("Decoded Message from cover", decoded_message)
        else:
           
            if not self.res_image:
                messagebox.showwarning("Warning", "Nothing found.")
                return
            decoded_message = self.decoding(self.res_image, self.lsb_count.get())
            if decoded_message:
                messagebox.showinfo("text from cover", decoded_message)
            else:
                messagebox.showinfo("Decoded Message", "No message found.")

    def decoding(self, img, bits_to_use):
        img_array = np.array(img).flatten()
        textbin = ''.join(format(img_array[i] & ((1 << bits_to_use) - 1), f'0{bits_to_use}b') for i in range(len(img_array)))
        retrievet = ""
        for i in range(0, len(textbin), 8):
            byte = textbin[i:i + 8]
            if len(byte) < 8:
                break
            char = chr(int(byte, 2))
            if char == '\0':  
                break
            retrievet += char
        return retrievet if all(0 <= ord(c) < 128 for c in retrievet) else None

    def save(self):
        if not self.res_image:
            messagebox.showwarning("Warning", "Nothing save.")
            return
        saving = filedialog.asksaveasfilename(defaultextension=".bmp", filetypes=[("BMP files", "*.bmp")])
        if saving:
            self.res_image.save(saving)

if __name__ == "__main__":
    root = Tk()
    app = TextInImage(root)
    root.mainloop()

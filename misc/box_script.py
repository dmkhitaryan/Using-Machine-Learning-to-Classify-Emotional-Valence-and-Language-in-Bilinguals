import fitz
import re

pdf_path = "/Users/jager/Downloads/trimmed_hsu.pdf"
output_path = "/Users/jager/Desktop/boxed_output.pdf"
output_file_path = "/Users/jager/Desktop/alt_english_passages.pdf"
#output_file_path = "/Users/jager/Desktop/valences.pdf"


def draw_bounding_box(pdf_path, output_path):
	file = fitz.open(pdf_path)
	for page in file:
		blocks = page.get_text("blocks")
		for b in blocks:
			print(b)
			rectangle = fitz.Rect(b[:4])
			print(rectangle)
			page.draw_rect(rectangle, color=(1,0,0), width=1.5)
			print("\n")

	file.save(output_path)

#draw_bounding_box(pdf_path, output_path)


def extract_text(pdf_path, x0, x1):
	file = fitz.open(pdf_path)
	output_file = open("alt_english_passages.txt", "w")

	for page in file:
		blocks = page.get_text("blocks")
		for b in blocks:
			if x0 <= b[0] <= x1 or x0 <= b[2] <= x1:
				text = b[4].replace('"', " ").replace("  ", " ")
				text = re.sub(r'@\s?', '', text)
				output_file.write(text + "\n")
		#column_blocks = [b for b in blocks if x0 <= b[0] <= x1 or x0 <= b[2] <= x1]
		#column_text = " ".join(block[4] for block in column_blocks)
		#column_text = column_text.replace('"', " ").replace("\n", " ")
		#output_file.write(column_text + "\n" + "\n")

		# text = b[4].replace('"', " ").replace("\n", " ").replace("  ", " ")

	#output_file.save(output_file_path)
	output_file.close()

x0, x1 = 263, 430 # English passage coordinates.
#x0, x1 = 433, 440 # Valences.
extract_text(pdf_path, x0, x1)
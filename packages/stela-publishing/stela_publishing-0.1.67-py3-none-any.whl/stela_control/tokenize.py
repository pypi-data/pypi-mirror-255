def split_text_to_paragraphs(text):
    paragraphs = text.split("\n")
    paragraphs = [paragraph for paragraph in paragraphs if paragraph.strip() != ""]
    return paragraphs

text = "Stela Control Dynamic es una solución innovadora para la gestión de proyectos y la optimización de la productividad.\nEsta herramienta de colaboración en línea ofrece una plataforma intuitiva para la gestión de proyectos, el seguimiento de tareas y la colaboración entre equipos.\nStela Control Dynamic le permite a los equipos de proyecto trabajar juntos de forma eficiente para alcanzar sus objetivos.\nEsta herramienta ofrece una interfaz intuitiva y fácil de usar para simplificar la gestión de proyectos. Además, ofrece una variedad de características útiles para mejorar la productividad, como el seguimiento de tareas, la asignación de recursos y la gestión de tiempos.\nStela Control Dynamic es la solución ideal para equipos de proyecto que buscan mejorar su productividad y optimizar el rendimiento de sus proyectos."
paragraphs = split_text_to_paragraphs(text)
for paragraph in paragraphs:
    print(paragraph)

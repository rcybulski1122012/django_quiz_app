from django import template

register = template.Library()


@register.simple_tag(name='questions_placeholder')
def get_number_of_questions_placeholder(questions):
    questions = questions or 10
    try:
        questions = int(questions)
    except ValueError:
        return 10

    if questions < 1:
        return 10
    elif questions > 20:
        return 20

    return questions


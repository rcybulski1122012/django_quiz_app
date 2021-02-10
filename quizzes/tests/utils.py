class FormSetTestMixin:
    def assertFormsetNumberOfFormsEqual(self, formset, expected):
        number_of_forms = len(formset.forms)
        self.assertEqual(number_of_forms, expected)
from amsdal_data.transactions import transaction


@transaction(name="{{ ctx.transaction_class_name }}")
def {{ ctx.transaction_method_name }}():
    # TODO: implementation here
    ...

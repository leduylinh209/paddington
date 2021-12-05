from import_export import resources, widgets

from service.merchandise.models import (Brand, Category, Country,
                                        InternalState, Product, Price,
                                        ProductCategory, ProductSupplier,
                                        Supplier, Unit)


class ProductResource(resources.ModelResource):

    def before_import_row(self, row, **kwargs):

        if row.get('brand'):
            brand, _ = Brand.objects.get_or_create(
                name=row['brand'],
                defaults={'code': row['brand']},
            )
            row['brand'] = brand.id

        if row.get('origin'):
            origin, _ = Country.objects.get_or_create(
                name=row['origin'],
                defaults={'code': row['origin']},
            )
            row['origin'] = origin.id

        if row.get('unit'):
            unit, _ = Unit.objects.get_or_create(
                name=row['unit'],
                defaults={'code': row['unit']},
            )
            row['unit'] = unit.id

        if row.get('internal_state'):
            internal_state, _ = InternalState.objects.get_or_create(
                name=row['internal_state'],
                defaults={'name': row['internal_state']},
            )
            row['internal_state'] = internal_state.id

    def after_save_instance(self, instance, using_transactions, dry_run):
        if not dry_run and not instance.internal_state:
            instance.internal_state, _ = InternalState.objects.get_or_create(
                code="raw",
                name="1. Sơ khai",
            )
            instance.save_without_signals()

    def after_import_row(self, row, row_result, **kwargs):

        if row.get('supplier_code'):
            supplier, _ = Supplier.objects.get_or_create(
                code=row['supplier_code'],
                defaults={
                    'name': row['supplier_code'],
                }
            )

            ProductSupplier.objects.get_or_create(
                supplier=supplier,
                product_id=row_result.object_id,
                defaults={
                    'supplier_sku': row['supplier_sku'],
                    'supplier_comment': row['supplier_comment'],
                    'supplier_collection': row['supplier_collection'],
                    'supplier_price': row['supplier_price'] or 0,
                }
            )

        if row.get('category'):
            category, _ = Category.objects.get_or_create(name=row['category'])

            ProductCategory.objects.get_or_create(
                category_id=category.id,
                product_id=row_result.object_id,
            )

    class Meta:
        model = Product
        import_id_fields = ('sku',)
        fields = (
            # Attributes
            'sku', 'name', 'packaging_specification', 'rrp', 'published',

            # Foreign keys
            'origin', 'brand', 'unit', 'internal_state',

            # Reverse foreign keys
            'category',
            'supplier_code', 'supplier_sku', 'supplier_comment',
            'supplier_collection', 'supplier_price',
        )


class PriceResource(resources.ModelResource):

    product = resources.Field(
        column_name='sku',
        attribute='product',
        widget=widgets.ForeignKeyWidget(Product, 'sku')
    )

    class Meta:
        model = Price
        import_id_fields = ('product', 'max_quantity')
        fields = ('product', 'price', 'max_quantity')

from sqlalchemy.orm import Session
from .models import Product, Supplier, ProductSupplier

def get_suppliers_by_product(db: Session, product_name: str):
    return db.query(Supplier.supplier_name, Supplier.contact_info).join(
        ProductSupplier, Supplier.supplier_id == ProductSupplier.supplier_id
    ).join(
        Product, Product.product_id == ProductSupplier.product_id
    ).filter(Product.product_name == product_name).all()

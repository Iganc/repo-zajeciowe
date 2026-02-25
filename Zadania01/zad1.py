class Product:
    def __init__(self, sku, name, category, unit_price_gross, vat_rate, qty):
        self.sku = sku
        self.name = name
        self.category = category
        self.unit_price_gross = unit_price_gross
        self.vat_rate = vat_rate
        self.qty = qty
class Client:
    def __init__(self, client_id, loyalty_level):
        self.c = client_id
        self.l = loyalty_level

client_info = {}
active_promotions = []

def calculatePrice(cart, client_info, active_promotions):
    pass
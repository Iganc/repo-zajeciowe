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

class Promotion:
    def apply(self, cart, client):
        return 0
    
class TwoPlusOnePromotion(Promotion):
    def apply(self, cart, client):
        discount = 0
        for product in cart.products:
            if product.qty >= 3:
                discount += product.unit_price_gross
        return discount

class CategoryPercentagePromotion(Promotion):
    def __init__(self, category, percent):
        self.category = category
        self.percent = percent

    def apply(self, cart, client):
        discount = 0
        for product in cart.products:
            if product.category == self.category:
                discount += product.unit_price_gross * product.qty * self.percent
        return discount

class FreeShippingPromotion(Promotion):
    def __init__(self, threshold, shipping_cost):
        self.threshold = threshold
        self.shipping_cost = shipping_cost

    def apply(self, cart, client):
        total = sum(p.unit_price_gross * p.qty for p in cart.products)
        if total >= self.threshold:
            return self.shipping_cost
        return 0

class PromotionEngine:
    def __init__(self, promotions):
        self.promotions = promotions

    def calculate_total(self, cart, client):
        subtotal = sum(p.unit_price_gross * p.qty for p in cart.products)

        total_discount = 0
        for promo in self.promotions:
            total_discount += promo.apply(cart, client)

        return subtotal - total_discount
    
class Receipt:
    def __init__(self, subtotal, discounts, shipping_cost):
        self.subtotal = subtotal
        self.discounts = discounts
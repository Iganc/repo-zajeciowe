class Product:
    def __init__(self, sku, name, category, unit_price_gross, vat_rate, qty):
        if unit_price_gross <= 0 or qty <= 0 or vat_rate < 0:
            raise ValueError()
        self.sku = sku
        self.name = name
        self.category = category
        self.unit_price_gross = unit_price_gross
        self.vat_rate = vat_rate
        self.qty = qty
        self.discounted_price = unit_price_gross

    def apply_discount(self, discount_per_unit):
        new_price = self.discounted_price - discount_per_unit
        if new_price < 1.0:
            self.discounted_price = 1.0
        else:
            self.discounted_price = new_price

class Client:
    def __init__(self, client_id, loyalty_level):
        self.client_id = client_id
        self.loyalty_level = loyalty_level

class Cart:
    def __init__(self, products):
        self.products = products

class Promotion:
    def apply(self, cart):
        pass

class CategoryPercentagePromotion(Promotion):
    def __init__(self, category, percent):
        self.category = category
        self.percent = percent

    def apply(self, cart):
        if self.category.lower() == "outlet":
            return
        for product in cart.products:
            if product.category == self.category and product.category.lower() != "outlet":
                discount = product.discounted_price * self.percent
                product.apply_discount(discount)

class FixedAmountCouponPromotion(Promotion):
    def __init__(self, amount, min_cart_value):
        self.amount = amount
        self.min_cart_value = min_cart_value

    def apply(self, cart):
        subtotal = sum(p.discounted_price * p.qty for p in cart.products)
        if subtotal >= self.min_cart_value:
            for product in cart.products:
                weight = (product.discounted_price * product.qty) / subtotal
                product_discount = (self.amount * weight) / product.qty
                product.apply_discount(product_discount)

class TwoPlusOnePromotion(Promotion):
    def __init__(self, sku_list):
        self.sku_list = sku_list

    def apply(self, cart):
        applied = False
        for product in cart.products:
            if product.sku in self.sku_list and product.qty >= 3:
                free_items = product.qty // 3
                total_discount = free_items * product.discounted_price
                discount_per_unit = total_discount / product.qty
                product.apply_discount(discount_per_unit)
                applied = True
        return applied

class FreeShippingPromotion(Promotion):
    def __init__(self, threshold, shipping_cost):
        self.threshold = threshold
        self.shipping_cost = shipping_cost

    def apply(self, cart):
        subtotal = sum(p.discounted_price * p.qty for p in cart.products)
        if subtotal >= self.threshold:
            return self.shipping_cost
        return 0

class CheapestProductHalfPricePromotion(Promotion):
    def __init__(self, category):
        self.category = category

    def apply(self, cart):
        valid_products = [p for p in cart.products if p.category == self.category and p.category.lower() != "outlet" and p.qty > 0]
        if valid_products:
            cheapest = min(valid_products, key=lambda p: p.discounted_price)
            discount_per_unit = (cheapest.discounted_price * 0.5) / cheapest.qty
            cheapest.apply_discount(discount_per_unit)

class PromotionEngine:
    def __init__(self, promotions):
        self.promotions = promotions

    def apply_promotions(self, cart):
        applied_two_plus_one = False
        for promo in self.promotions:
            if isinstance(promo, TwoPlusOnePromotion):
                if promo.apply(cart):
                    applied_two_plus_one = True

        shipping_discount = 0
        for promo in self.promotions:
            if isinstance(promo, TwoPlusOnePromotion):
                continue
            if isinstance(promo, FixedAmountCouponPromotion):
                if not applied_two_plus_one:
                    promo.apply(cart)
            elif isinstance(promo, FreeShippingPromotion):
                shipping_discount = promo.apply(cart)
            else:
                promo.apply(cart)
        
        return shipping_discount

class Receipt:
    def __init__(self, cart, shipping_cost, shipping_discount):
        self.cart = cart
        self.shipping_cost = shipping_cost
        self.shipping_discount = shipping_discount

    def generate(self):
        lines = []
        total_gross = 0
        total_net = 0
        total_vat = 0
        total_savings = 0

        for p in self.cart.products:
            original_total = p.unit_price_gross * p.qty
            discounted_total = p.discounted_price * p.qty
            savings = original_total - discounted_total
            net_price = discounted_total / (1 + p.vat_rate)
            vat_amount = discounted_total - net_price

            total_gross += discounted_total
            total_net += net_price
            total_vat += vat_amount
            total_savings += savings

            lines.append({
                "sku": p.sku,
                "name": p.name,
                "qty": p.qty,
                "original_price_unit": p.unit_price_gross,
                "discounted_price_unit": round(p.discounted_price, 2),
                "line_savings": round(savings, 2)
            })

        final_shipping = max(0, self.shipping_cost - self.shipping_discount)
        total_gross += final_shipping

        return {
            "lines": lines,
            "summary": {
                "total_gross": round(total_gross, 2),
                "total_net": round(total_net, 2),
                "total_vat": round(total_vat, 2),
                "shipping_cost": final_shipping,
                "total_savings": round(total_savings + self.shipping_discount, 2)
            }
        }
import train_model

sf = train_model.SlotFilling()
slot = sf.decode("請問得青光眼會怎麼樣")
print (slot)
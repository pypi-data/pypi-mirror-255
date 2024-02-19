# Shopee API Wrapper - Not official

## Install

```
pip install shopee-api-wrapper
```

## Quickstart

## Fetch product

```py
from shopee_api import Shopee

def main():
    # Configuring origin of endpoints
    shopee = Shopee(origin_url = "https://shopee.com.br")

    # Fetching product by URL
    data = shopee.fetch_product(url = "https://shopee.com.br/Videogame-Stick-10mil-2-Controles-Sem-Fio-Console-Original-Portatil-Jogos-Retro-Antigo-Marisa-i.400311012.18265078100")

    # Printing data to the terminal
    print(data)

if __name__ == "__main__":
    main()
```

*Detail: you don't need to do this `def main(): ...;if __name__ == "__main__": main()` structure, it's just good practice :)*

That's it for now, if you have any suggestions, don't hesitate to create an Issue
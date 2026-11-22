Attached are saved Delhaize favorites-list pages (.htm). Write code to parse them and give me ONE CSV
file named favorites.csv with columns: list,name,url,image,price_when_saved (all fields in double quotes).
For each file:
- list = text of the page's <h1>. If a file has no product tiles, skip it and tell me.
- each product is an element with data-testid="product-block".
- name = aria-label of its a[data-testid="product-block-image-link"]
- url = href of that link, without anything after "?"
- image = first https://static.delhaize.be/... URL in the srcset of img[data-testid="product-block-image"],
  without the query string, then append "?imwidth=300" (do NOT use the local ./..._files/ src)
- price_when_saved = from the aria-label of [data-testid="product-block-price"] ("Prijs: 3 euro 55 cent" -> 3.55);
  empty if absent (unavailable products)
Report the number of products per list, and don't invent or skip anything.

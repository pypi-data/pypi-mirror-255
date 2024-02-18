def among_us(PlayersNumber: int, lang="eng"):
    if type(PlayersNumber) != int:
        raise TypeError
    elif PlayersNumber <= 2:
        print("Players number should be greater than 2")
    else:
        from random import choice
        if lang == "eng":
            players = {}
            words = ["Table", "Chair", "Lamp", "Sofa", "Bookshelf", "Television", "Remote control", "Clock", "Mirror", "Vase", 
                "Pillow", "Blanket", "Curtain", "Rug", "Desk", "Computer", "Mouse", "Keyboard", "Monitor", "Printer", 
                "Refrigerator", "Stove", "Microwave", "Toaster", "Dishwasher", "Plate", "Fork", "Knife", "Spoon", "Cup", 
                "Vase", "Plant", "Picture frame", "Candle", "Basket", "Tray", "Towel", "Soap", "Shampoo", "Toothbrush", 
                "Toothpaste", "Towel rack", "Toilet", "Sink", "Mirror", "Soap dispenser", "Towel holder", "Shower", "Bathtub", 
                "Bed", "Mattress", "Pillowcase", "Blanket", "Alarm clock", "Dresser", "Wardrobe", "Hanger", "Shoes", 
                "Slippers", "Closet", "Coat rack", "Umbrella", "Hat", "Gloves", "Scarf", "Sunglasses", "Wallet", 
                "Keychain", "Purse", "Backpack", "Suitcase", "Briefcase", "Pen", "Pencil", "Notebook", "Eraser", 
                "Stapler", "Tape", "Scissors", "Glue", "Calculator", "Ruler", "Folder", "Paperclip", "Document", 
                "Envelope", "Stamp", "Trash can", "Recycling bin", "Laundry basket", "Iron", "Ironing board", 
                "Detergent", "Broom", "Dustpan", "Mop", "Bucket", "Vacuum cleaner", "Cleaning cloth", "Air freshener",
                "Sofa", "Television", "Heater", "Fan", "Air conditioner", "Bookshelf", "Console", "Speaker", "Book", 
                "Newspaper", "Magazine", "CD", "DVD", "Video game", "Camera", "Camcorder", "Phone", "Tablet", "Headphones", 
                "Charger", "Battery", "Cable", "Wall clock", "Pocket watch", "Wristwatch", "Jewelry", "Wallet", 
                "Card", "Paper", "Fountain pen", "Brush", "Paint", "Color pencil", "Brush", "Canvas", "Easel", 
                "Ink", "Shelf", "Library", "Chest of drawers", "Makeup mirror", "Perfume", "Jewelry box", 
                "Cushion", "Throw", "Tablecloth", "Dishware", "Cutlery", "Kitchen", "Glass", "Coffee cup", "Tea cup", 
                "Plate", "Bowl", "Tablecloth", "Napkin", "Shower curtain", "Heated towel rack", "Toilet", 
                "Sink", "Bathtub", "Shower", "Towel", "Bathrobe", "Hair dryer", "Hair straightener", "Hairbrush", 
                "Makeup", "Eyeshadow", "Lipstick", "Mascara", "Makeup brush", "Cotton swab", "Makeup remover", 
                "Moisturizer", "Deodorant", "Shampoo", "Conditioner", "Shower gel", "Soap", "Lotion", "Lip balm", 
                "Tissue", "Trash bag", "Laundry basket", "Laundry", "Fabric softener", "Ironing board", "Iron", 
                "Detergent", "Broom", "Dustpan", "Bucket", "Cloth", "Vacuum cleaner", "Brush", "Hanger", "Coat rack", 
                "Shoe rack", "Welcome mat", "Doormat", "Umbrella", "Cap", "Hat", "Sunglasses", "Scarf", "Gloves", 
                "Watch", "Necklace", "Bracelet", "Ring", "Wallet", "Cardholder", "Key", "Phone", "Keychain", 
                "Desk lamp", "Flashlight", "Table lamp", "Chandelier", "Light bulb", "Picture frame", "Wall mirror", 
                "Statue", "Plant", "Flower", "Vase", "Photograph", "Painting", "Sculpture", "Wall clock", "Alarm clock", 
                "Pendulum", "Watch", "Socks", "Tights", "Scarf", "Beanie", "Gloves", "Pajamas", "Nightgown", "Bathrobe", 
                "Towel", "Bath mat", "Scale", "Toothbrush", "Toothpaste", "Dental floss", "Tissues", "Toilet paper", 
                "Toilet brush", "Deodorant", "Shampoo", "Conditioner", "Shower gel", "Soap", "Moisturizer", "Lip balm", 
                "Tissues", "Waste bin", "Laundry basket", "Laundry detergent", "Fabric softener", "Ironing board", 
                "Iron", "Detergent", "Broom", "Dustpan", "Bucket", "Cloth", "Vacuum cleaner", "Brush", "Hanger", 
                "Coat rack", "Shoe rack", "Welcome mat", "Doormat", "Umbrella", "Cap", "Hat", "Sunglasses", 
                "Scarf", "Gloves", "Watch", "Necklace", "Bracelet", "Ring", "Wallet", "Cardholder", "Key", "Phone", 
                "Keychain"]
            randomize = choice(words)
            word = [randomize] * (PlayersNumber-1)
            word.append("imposter")
            for i in range(PlayersNumber):
                player = input("Enter your name:\n>>    ")
                players[i] = player
                identity = choice(word)
                if identity == "imposter":
                    imposter = i
                    word.remove("imposter")
                    pass_the_phone = input("\033[91mYOU ARE THE IMPOSTER\n\033[0mPress enter and pass the phone to another player: ")
                    print("\n" * 4000)
                else:
                    pass_the_phone = input(f"\033[92mYOU ARE A CREWMATE\n\033[0mThe word is {identity}\nPress enter and pass the phone to another player: ")
                    word.remove(word[0])
                    print("\n" * 4000)
            while len(players) > 2 and imposter in players:
                start_voting = input("Press enter when you are going to start voting for the imposter: ")
                print(players, "\n Each Player vote to what he want using player's id!")
                votes = {}
                for i in range(len(players)):
                    id = int(input("\nWhich Player you are going to vote?\n>>    "))
                    if id in votes:
                        votes[id] += 1
                    else:
                        votes[id] = 1
                out = max(votes, key=votes.get)
                found_duplicate = False
                for key1, value1 in votes.items():
                    for key2, value2 in votes.items():
                        if key1 != key2 and value1 == value2:
                            found_duplicate = True
                            print("No player has been kicked from the game")
                            break
                    if found_duplicate:
                        break
                if not found_duplicate:
                    print(players[out], "was kicked from the game")
                    if out == imposter:
                        print(players[out], "is the imposter\n\033[92mCrewmates won!")
                        break
                    else:
                        print(players[out], "is not the imposter")
                        players.pop(out)
            else:
                print(players[imposter], "was the imposter\n\033[91mImposter won!")
        elif lang == "fr":
            players = {}
            words = ["Table", "Chaise", "Lampe", "Canapé", "Étagère", "Télévision", "Télécommande", "Horloge", "Miroir", "Vase", 
                "Oreiller", "Couverture", "Rideau", "Tapis", "Bureau", "Ordinateur", "Souris", "Clavier", "Moniteur", 
                "Imprimante", "Réfrigérateur", "Cuisinière", "Micro-ondes", "Grille-pain", "Lave-vaisselle", "Assiette", 
                "Fourchette", "Couteau", "Cuillère", "Tasse", "Plante", "Cadre photo", "Bougie", "Panier", "Plateau", 
                "Serviette", "Savon", "Shampoing", "Brosse à dents", "Dentifrice", "Porte-serviettes", "Toilette", "Évier", 
                "Distributeur de savon", "Porte-serviettes", "Douche", "Baignoire", "Lit", "Matelas", "Taie d'oreiller", 
                "Dresser", "Armoire", "Cintre", "Chaussures", "Chaussons", "Placard", "Porte-manteau", "Parapluie", "Chapeau", 
                "Gants", "Écharpe", "Lunettes de soleil", "Portefeuille", "Porte-clés", "Sac à main", "Sac à dos", "Valise", 
                "Mallette", "Stylo", "Crayon", "Cahier", "Gomme", "Agrafeuse", "Ruban adhésif", "Ciseaux", "Colle", "Calculatrice", 
                "Règle", "Dossier", "Trombone", "Document", "Enveloppe", "Timbre", "Poubelle", "Poubelle de recyclage", 
                "Panier à linge", "Fer à repasser", "Planche à repasser", "Détergent", "Balai", "Pelle à poussière", 
                "Serpillière", "Seau", "Aspirateur", "Chiffon de nettoyage", "Assainisseur d'air", "Canapé", "Télévision", 
                "Radiateur", "Ventilateur", "Climatiseur", "Étagère à livres", "Console", "Haut-parleur", "Livre", "Journal", 
                "Magazine", "CD", "DVD", "Jeu vidéo", "Appareil photo", "Caméra", "Téléphone", "Tablette", "Casque", "Chargeur", 
                "Batterie", "Câble", "Horloge murale", "Horloge de poche", "Montre", "Bijoux", "Porte-monnaie", "Carte", 
                "Papier", "Stylo-plume", "Pinceau", "Peinture", "Crayon de couleur", "Pinceau", "Toile", "Chevalet", 
                "Encre", "Étagère", "Bibliothèque", "Commode", "Miroir de maquillage", "Parfum", "Boîte à bijoux", 
                "Coussin", "Jeté", "Nappe", "Vaisselle", "Couverts", "Cuisine", "Verre", "Tasse à café", "Tasse à thé", 
                "Plat", "Bol", "Nappe", "Serviette de table", "Rideau de douche", "Porte-serviettes chauffant", "Toilette", 
                "Lavabo", "Baignoire", "Douche", "Serviette", "Peignoir", "Sèche-cheveux", "Lisseur", "Brosse à cheveux", 
                "Maquillage", "Fard à paupières", "Rouge à lèvres", "Mascara", "Pinceau de maquillage", "Coton-tige", 
                "Démaquillant", "Crème hydratante", "Parapluie", "Pantalon", "Chemise", "Robe", "Chaussures", "Sac", 
                "Chapeau", "Gants", "Écharpe", "Lunettes de soleil", "Ceinture", "Montre", "Boucle d'oreille", "Collier", 
                "Bracelet", "Bague", "Portefeuille", "Porte-cartes", "Clé", "Téléphone", "Porte-clés", "Lampe de bureau", 
                "Lampe de poche", "Lampe de table", "Lustre", "Ampoule", "Cadre photo", "Miroir mural", "Statue", "Plante", 
                "Fleur", "Vase", "Photographie", "Peinture", "Sculpture", "Horloge murale", "Réveil", "Pendule", "Montre", 
                "Chaussettes", "Collants", "Écharpe", "Bonnet", "Gants", "Pyjama", "Chemise de nuit", "Peignoir", "Serviette", 
                "Tapis de bain", "Pèse-personne", "Brosse à dents", "Dentifrice", "Fil dentaire", "Mouchoirs", "Papier toilette", 
                "Brosse à toilette", "Déodorant", "Shampooing", "Après-shampooing", "Gel douche", "Savon", "Crème hydratante", 
                "Baume à lèvres", "Mouchoirs en papier", "Sac poubelle", "Panier à linge", "Lessive", "Adoucissant", "Planche à repasser", 
                "Fer à repasser", "Détergent", "Balai", "Pelle à poussière", "Seau", "Chiffon", "Aspirateur", "Brosse", "Cintre", 
                "Porte-manteau", "Étagère à chaussures", "Tapis d'entrée", "Paillasson", "Parapluie", "Casquette", "Chapeau", "Lunettes de soleil", 
                "Écharpe", "Gants", "Montre", "Collier", "Bracelet", "Bague", "Portefeuille", "Sac à main", "Sac à dos", "Valise", "Mallette"]
            randomize = choice(words)
            word = [randomize] * (PlayersNumber-1)
            word.append("imposter")
            for i in range(PlayersNumber):
                player = input("Enter your name:\n>>    ")
                players[i] = player
                identity = choice(word)
                if identity == "imposter":
                    imposter = i
                    word.remove("imposter")
                    pass_the_phone = input("\033[91mYOU ARE THE IMPOSTER\n\033[0mPress enter and pass the phone to another player: ")
                    print("\n" * 4000)
                else:
                    pass_the_phone = input(f"\033[92mYOU ARE A CREWMATE\n\033[0mThe word is {identity}\nPress enter and pass the phone to another player: ")
                    word.remove(word[0])
                    print("\n" * 4000)
            while len(players) > 2 and imposter in players:
                start_voting = input("Press enter when you are going to start voting for the imposter: ")
                print(players, "\n Each Player vote to what he want using player's id!")
                votes = {}
                for i in range(len(players)):
                    id = int(input("\nWhich Player you are going to vote?\n>>    "))
                    if id in votes:
                        votes[id] += 1
                    else:
                        votes[id] = 1
                out = max(votes, key=votes.get)
                found_duplicate = False
                for key1, value1 in votes.items():
                    for key2, value2 in votes.items():
                        if key1 != key2 and value1 == value2:
                            found_duplicate = True
                            print("No player has been kicked from the game")
                            break
                    if found_duplicate:
                        break
                if not found_duplicate:
                    print(players[out], "was kicked from the game")
                    if out == imposter:
                        print(players[out], "is the imposter\n\033[92mCrewmates won!")
                        break
                    else:
                        print(players[out], "is not the imposter")
                        players.pop(out)
            else:
                print(players[imposter], "was the imposter\n\033[91mImposter won!")
        elif lang == "ar":
            players = {}
            words = [
                "طاولة", "كرسي", "مصباح", "صوفا", "رف الكتب", "تلفاز", "جهاز التحكم عن بعد", "ساعة", "مرآة", "زهرية",
                "وسادة", "بطانية", "ستارة", "سجادة", "مكتب", "كمبيوتر", "فأرة", "لوحة المفاتيح", "شاشة العرض", "طابعة",
                "ثلاجة", "موقد", "ميكروويف", "محمصة", "غسالة صحون", "صحن", "شوكة", "سكين", "ملعقة", "كوب",
                "زهرية", "نبات", "إطار الصورة", "شمعة", "سلة", "صينية", "منشفة", "صابون", "شامبو", "فرشاة الأسنان",
                "معجون الأسنان", "رف المناشف", "مرحاض", "حوض", "مرآة", "موزع الصابون", "حامل المناشف", "دش", "حوض الاستحمام",
                "سرير", "فراش", "وسادة", "بطانية", "منبه", "خزانة الملابس", "خزانة", "شماعة", "أحذية",
                "شباشب", "خزانة", "رف معاطف", "مظلة", "قبعة", "قفازات", "وشاح", "نظارات شمسية", "محفظة",
                "سلسلة المفاتيح", "محفظة", "حقيبة ظهر", "حقيبة", "حقيبة", "قلم", "قلم رصاص", "دفتر", "ممحاة",
                "مدبب", "شريط", "مقص", "غراء", "آلة حاسبة", "مسطرة", "مجلد", "مشبك ورق", "وثيقة",
                "ظرف", "طابعة", "سلة المهملات", "صندوق إعادة التدوير", "سلة الملابس", "مكواة", "مكتب المكواة",
                "منظف", "مكنسة", "جارف الغبار", "ممسحة", "دلو", "مكنسة كهربائية", "قماش تنظيف", "معطر الهواء",
                "صوفا", "تلفزيون", "سخان", "مروحة", "مكيف هواء", "رف الكتب", "جهاز اللعب", "مكتب", "كتاب",
                "جريدة", "مجلة", "قرص مدمج", "دي في دي", "لعبة فيديو", "كاميرا", "كاميرا فيديو", "هاتف", "جهاز لوحي",
                "سماعات", "شاحن", "بطارية", "كابل", "ساعة حائط", "ساعة جيب", "ساعة يد", "مجوهرات", "محفظة",
                "بطاقة", "ورق", "قلم حبر", "فرشاة", "طلاء", "ألوان ملونة", "فرشاة", "قماش", "مثبتات اللوحات",
                "حبر", "رف", "مكتبة", "منضدة", "مرآة المكياج", "عطر", "صندوق مجوهرات", "وسادة", "غطاء",
                "مفارش الطاولة", "أواني", "أدوات الطعام", "أدوات المائدة", "مطبخ", "زجاجة", "كوب القهوة", "كوب الشاي",
                "صحن", "وعاء", "مفارش الطاولة", "منديل", "ستارة الدش", "سخان المناشف", "مرحاض", "حوض", "حوض الاستحمام",
                "دش", "منشفة", "روب الاستحمام", "مجفف الشعر", "مملس الشعر", "فرشاة الشعر", "مكياج", "ظلال العيون",
                "أحمر الشفاه", "مسكارا", "فرشاة المكياج", "عود القطن", "إزالة المكياج", "مرطب", "مزيل العرق", "شامبو",
                "بلسم", "جل الاستحمام", "صابون", "لوشن", "مرطب الشفاه", "مناديل", "كيس القمامة", "سلة الملابس",
                "غسل الملابس", "منعم الأقمشة", "مكواة الملابس", "مكتب المكواة", "مكواة", "مكنسة", "جارف الغبار", "دلو",
                "قماش"]
            randomize = choice(words)
            word = [randomize] * (PlayersNumber-1)
            word.append("imposter")
            for i in range(PlayersNumber):
                player = input("Enter your name:\n>>    ")
                players[i] = player
                identity = choice(word)
                if identity == "imposter":
                    imposter = i
                    word.remove("imposter")
                    pass_the_phone = input("\033[91mYOU ARE THE IMPOSTER\n\033[0mPress enter and pass the phone to another player: ")
                    print("\n" * 4000)
                else:
                    pass_the_phone = input(f"\033[92mYOU ARE A CREWMATE\n\033[0mThe word is {identity}\nPress enter and pass the phone to another player: ")
                    word.remove(word[0])
                    print("\n" * 4000)
            while len(players) > 2 and imposter in players:
                start_voting = input("Press enter when you are going to start voting for the imposter: ")
                print(players, "\n Each Player vote to what he want using player's id!")
                votes = {}
                for i in range(len(players)):
                    id = int(input("\nWhich Player you are going to vote?\n>>    "))
                    if id in votes:
                        votes[id] += 1
                    else:
                        votes[id] = 1
                out = max(votes, key=votes.get)
                found_duplicate = False
                for key1, value1 in votes.items():
                    for key2, value2 in votes.items():
                        if key1 != key2 and value1 == value2:
                            found_duplicate = True
                            print("No player has been kicked from the game")
                            break
                    if found_duplicate:
                        break
                if not found_duplicate:
                    print(players[out], "was kicked from the game")
                    if out == imposter:
                        print(players[out], "is the imposter\n\033[92mCrewmates won!")
                        break
                    else:
                        print(players[out], "is not the imposter")
                        players.pop(out)
            else:
                print(players[imposter], "was the imposter\n\033[91mImposter won!")
        else:
            print("languages availble are ('eng': English / 'fr': French / 'ar': Arabic)")
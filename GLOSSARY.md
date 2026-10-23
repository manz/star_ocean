# Star Ocean (SNES): JP → FR glossary

Translation choices made by the original community team, extracted from their data, to keep new work consistent.

Sources: `SO_items_fra.txt` (names8 `$00`, battle16 `$01`, menu16 `$03`), `Patch PRE ALPHA/TXT/menu.txt` (labels8),
`text/{jp,fr}/scene_NN.xml` (dialog: `[color][0x4]` highlights, `[pos]` signs, speakers). Column "8x8" is the short menu
name (names8/labels8), "16x16" the long name (battle16), "desc" the name heading the menu16 description when it differs.
`×N` counts dialog occurrences.

## Conventions

- **Speaker**: JP `名前「…` → FR name alone on the page's first line, no 「」, text on the next line.
- **Punctuation**: space before `?` / `!` in dialog (2505 vs 339 without). Menu labels are mixed
  (`D'accord ?` but `Utiliser sur qui?`). `・・・` → `...` (never `…`). Straight quotes `"…"`, no « ». `♪` → `[NOTE]`, `♥` kept.
- **Tu / vous**: both (≈800 tu/toi/te forms, ≈920 vous). The game addresses the player with *vous*
  (`Quel objet allez-vous utiliser?`, `Vous avez appris l'arcane…`); party members mostly *tutoient* each other.
- **Capitalisation**: generic part lowercase in dialog (`temple de Parj`, `château d'Astral`, `royaume de Moore`);
  `[pos]` signs capitalised (`Château d'Astral`, `Port de Tropp`). Music titles in CAPS without accents.
- **8x8 names**: drawn by the 8x8 VWF (`tools/vwf8.py`). Items fit the item list's name field, 64 px (8 cells):
  spaced words (`Bague fée`, `Marteau forge`, `Épée longue+1`), abbreviated only when the full name does not fit.
  Spells ≤ 10 chars, special moves ≤ 11. To fit those:
  - CamelCase compounds, no space;
  - head noun cut to initial + dot: `É.` épée, `B.` bague/bâton, `C.` capel/contre, `Gr.` grève, `O.` orbe, `D.` danse/double,
    `Pg.` poing, `Id.` idole, `Fig.` figurine, `Col.` collier, `Arm.` armure, `Cr.`/`Crist.` cristal;
  - initials as suffix: `GO` Grande Ourse, `DA`/`DN`/`DR` dragon azur/noir/rouge, `OV` oiseau vermillon;
  - `+1`/`+2` kept, `MK2` → `V2`.
- **Item series by suffix**: ポーション/ボトル/ポット → `-ixir` (Bullixir, Fusixir, Fruitixir); ボム → `-otov`
  (Toxotov, Puantotov, Psychotov, Flambotov; stronger = `+`); キュア… → `Anti-`; ミスト → `Brume …`; シロップ → `Sirop …`.
- **Unidentified**: `？WEAPON` → `?Arme`, `？GUARD` → `?Défense`, `？ITEM` → `?Réserve`, `？JEM` → `?Gemme`,
  `？JEWELRY` → `?Bijou`, `？HERB` → `?Herbe`, `？FOOD` → `?Vivres`.
- **Enemies**: French or classic tabletop names (Otyugh, Grell, Aarakocra, Yochlol), with pop-culture nods
  (Shai-Hulud, Sauron, Arsène, Hannibal). `…シェイプ` series → `-oïde`.

## Characters

### Party

| JP full | JP 8x8 | FR full (names8) | FR 8x8 | Dialog | note |
|---|---|---|---|---|---|
| ラティクス | ラティ | Ratix | Raty | Raty ([nick:]), Ratix ([name:]) | |
| ミリー | ミリー | Millie | Milly | Millie | full ≠ short |
| ドーン | ドーン | Dorn | Dorn | Dorn | |
| ロニキス | ロニキス | Ronixs | Ronix | Ronixs | 6 letters: the WRAM name slot |
| イリア | イリア | Iria | Iria | Iria | |
| シウス | シウス | Cius | Cius | Cius | |
| ヨシュア | ヨシュア | Joshua | Joshua | Joshua | |
| ティニーク | ティニ | Tinek | Tini | Tinek | |
| マーヴェル | マーヴェ | Marvel | Marv | Marvel | |
| アシュレイ | アシュ | Ashlay | Ash | Ashlay | |
| ペリシー | ペリシー | Périsy | Péri | Périsy | 6 letters: the WRAM name slot |
| フィア | フィア | Fear | Fear | Fear | |
| ルーン | ルーン | Rune | Dorn | - | 8x8 `$000D` = "Dorn" (bug) |

Dialog inserts read the WRAM name records (`tools/party_names.py`, `src/dialog/names.s`): `[nick:]` is Ratix's
nickname but every other character's name, so a name the player enters shows. Names fit 6 letters, nicknames 4.

### Recurring and named NPCs

| JP | FR | note |
|---|---|---|
| パフィ | Puffy | ×57 |
| 説明員 | Mentor | ×48, guild |
| ギルドマスター | Maître de la guilde | ×37 |
| アドバイザー | Conseiller | ×14 (also Entraîneur ×5) |
| 解説マン | Commentateur | ×17, arena |
| ヴァン国王 | Roi de Van | ×32 |
| アストラル国王 | Roi d'Astral | ×12 |
| ムーア国王 | Roi de Moore | |
| シルヴァラント国王 | Roi de Sylvalant | |
| 国王 / 王妃・妃 | Roi / Reine | |
| 大臣 | Chancelier | ×23 |
| 大臣ボルク | Chancelier Bolc | |
| 真紅の楯 | Bouclier écarlate | ×27 |
| ドクター | Docteur | ×22 |
| 提督 / ベイズ提督 | Amiral | |
| 艦長 | Capitaine | |
| バダム | Badam | |
| ライアス | Ryas | |
| ジエ / ジエ・リヴォース | Jay (dialog) / Jie Revorse (8x8) | see Inconsistencies |
| ネオ・リヴォース | Neo Revorse | |
| デル・アーガスィ | Del Argasi | |
| アスモデウス | Asmodeus | |
| イヴィーナ | Ivina | |
| フォスター | Foster | |
| ルシオ / 宿の息子ルシオ | Lucio | |
| マルトス | Maltos | |
| 船乗りベン | Ben le Marin | |
| 宿の女将ジュディ | Judy | |
| レゾニア密使 | Ambassadeur résonien | |
| 旅人ラドル | Raddle le voyageur / l'aventurier | |
| 年頃のリリー | Petite Lily | |
| 年頃のアリサ | Jeune femme Alisa | |
| メイリィ | Marie (8x8, ×4) / Mary (×2) | |
| メアリ | Mary | |
| ダースウィドウ | Veuve noire | 8x8 ダースウィドゥ = Maïtïka |
| 親分ベアード | Chef Baird | |
| 盗賊ビッツ | Voleur Bitts | |
| ヴェルカント / ヴェルカントのボス | Velcant / Chef Velcant | 8x8: Velcanto |
| プリシラ | Priscilla | |
| ガブリエル | Gabrielle | |
| レスフィーナ | Seraphina | |
| ゲディス | Gedis | |
| ウォルザ | Wolza | |
| パンクポンク | Panku Ponk (8x8) / PankPonk | |
| フレーゼ / 食料店のおばさんフレーゼ | Mme Fraise | |
| ソフィア | Sophia | |
| レミア / 知識人レミア | Lemia / Érudite Lemia | |
| ディーン | Dean | |
| 魚屋のブラド | Poissonnier Brad | |
| テリー / 片目のテリー | Terry / Terry le borgne | |
| ロザリオ | Rosario | |
| ミューキィ / ミューキー | Myuki | |
| 衛兵ロイド / ロイド | Garde Roméo / Roméo | 博学のロイド = Loid l'étudiant |
| メイドのジュリオ | Servante Juliette | |
| 傭兵トク | Mercenaire Toku | |
| 宮廷紋章術師 | Mage | |
| 行商人サンタ | Santa, camelot / Marchand Ambulant Santa | |
| 食べ物屋テムジン | Temujin l'épicier / Restaurant Temjin | |
| 道具屋ペーター | Peter le vendeur | |
| 道具屋ウォルサム | Quincaillerie Wolsam | |
| リザ | Liza | |
| シーナ / セレナ / エリス / ルルー / ジュン | Shina / Selena / Eris / Lulu / Jun | |
| チェルシー | Chelsea | |
| エアリナ | Elina | |
| ウェルディー / ヴァイア | Weldy / Vaia | |
| トんでる娘リーザ | Leeza | |
| 町娘エリオット | Eliotte | |
| 父親ダラン / 息子ロト | Dalan / Lot | |
| 賢者グイン / グレイス / ピロン / リッド / ヴァンク / サーク | Xerus / Sage Grace / Pilon / Riddo / Vank / Starck | "X le sage" pattern |
| 鍛冶師ギム | Gim le forgeron | |
| 剣士ロウェル | Rowell le chevalier | |
| 騎士ゼル / 騎士クルト | Zel / Kurt le chevalier | |
| 衛兵トーク / 衛兵ヤーマ | Tork / Yarma le garde | |
| 傭兵ウォルス / ステア / ラルフ | Worus le garde / Sutea / Ralph le mercenaire | |
| 冒険者ルドア / メイアー / ジル / クマ / ピロン / ユウ | Rudoa / Meia / Jiru / Kuma / Pilon / Yuu (l'aventurier) | |
| 画家ジョン / 学者カノイ / 若い学者ベルナー | Jon le peintre / Kanoi l'étudiant / Belnar l'écolier | |
| 宮廷音楽家オサトー | Osato le musicien | |
| はき物屋ビクトル / 武器屋モーガン | Victor le cordonnier / Morgan l'armurier | |
| 傷心のエノル | Enoru au cœur brisé | |
| ピコ / ナノ / メガ / ギガ | Pico / Nano / Mega / Giga | |
| すとれと | Sutoreto | developers (Tri-Ace room) |
| まさきんぐ / けんいち / ささっち / みやもと / かわかみ / にしたに / まりちー / はまやん / とく / やまちゃん / はっしぃ / じゅん | Masaking / Kenichi / Sasatchi / Miyamoto / Kawakami / Nishitani / Marichii / Hamayan / Toku / Yama-chan / Hasshii / Jin | romaji |
| トライアの一人 | Dev Tri-Ace / Membre Tri-ace | |

Generic roles: 衛兵 Garde, 兵士 Soldat, 男 Homme, 女 Femme, 娘/少女 Fille, 若者 Jeune homme, 老婆 Vieille femme,
老人 Vieil homme, 船員/船乗り Marin, 冒険者 Aventurier, 宿屋の主人 Aubergiste, 店の親父/マスター Barman, 剣士 Chevalier/Combattant,
少年 Garçon, 子供 Gamin/Enfant, メイド Servante, 魔物 Monstre, 傭兵 Mercenaire, 学者 Étudiant, 乗組員 Membre de l'équipage,
所長 Ancien, 案内N Information N, 道具屋 Vendeur.

## Places

### Planets, space

| JP | FR |
|---|---|
| ローク | Roak |
| 地球 | Terre |
| 惑星 | planète |
| 連邦 / 地球連邦 | Fédération |
| レゾニア | Resonia (adj. résonien) |
| ファーゲット | Farget |
| カルナス（戦艦） | Calnus |
| カルナス戦艦ブリッジ | Pont du Calnus |
| カルナス戦艦士官部屋 | Salle des officiers - Calnus |
| カルナス戦艦医療施設 | Centre médical du Calnus |
| カルナス戦艦転送室 | Calnus - Salle du transporteur |
| カルナス戦艦ホロデッキ | Holocube du Calnus |
| エレベーターポット | Ascenseur |
| 星の船落下地点 | Zone de crash du vaisseau |
| 時空研究所 | Laboratoire de recherches quantiques |
| 魔界 | Monde démoniaque |

### Kingdoms, towns, dungeons

| JP | FR | note |
|---|---|---|
| アストラル | Astral | ×27 |
| アストラル王国 | royaume d'Astral | |
| アストラル城 | château d'Astral | |
| アストラル城下町 | ville fortifiée d'Astral / Ville du château d'Astral | |
| アストラル城門 | Portes du château Astral | |
| アストラル城下町の港 | Port d'Astral | |
| アストラル洞窟 | grotte(s) d'Astral | |
| ポートミス / ポートミスの港 | Portmith / Port de Portmith | |
| シルヴァラント | Sylvalant | |
| シルヴァラント城下（町） | ville fortifiée de Sylvalant | |
| シルヴァラント遺跡 | Ruines de Sylvalant | |
| シルヴァラントの港 | Port de Sylvalant | |
| ヴァン | Van | |
| ヴァン・イ・イル（城下町/城/城門） | Van I Il (Ville fortifiée de / Château de) | |
| ムーア / ムーア王国 | Moore / royaume de Moore | |
| ムーア城 / ムーア城門 | château de Moore / Portes de Moore | |
| パージ神殿 | temple de Parj | |
| パージ神殿深層部 | Sanctuaire de Parj | |
| タトローイ | Tatroï | |
| タトローイ闘技場 | Arène de Tatroï | |
| タトローイ闘技場控え室 | Entrée de l'arène de Tatroï | |
| タトローイ運河船のりば | Quai de chargement de Tatroï | |
| イオニス | Ionis | |
| メトークス山 / 山頂 | Mont Métox / Sommet du mont Métox | "mont" lowercase in running text: le mont Métox |
| クール / クール村 | Laponia / Village de Laponia | "cool" localised |
| ホット | Thermonia | "hot" localised |
| トロップ / トロップの港 | Tropp / Port de Tropp | |
| オタニム / オタニムの港 | Otanim / Port d'Otanim | |
| クラトス / クラトスの町 | Clatos / Ville de Clatos | |
| エクダート / エクダートの港 | Ecdart / Port d'Ecdart | |
| ドゥルス | Dulce | |
| クラート（村） | Crat / Village de Crat | |
| 七星の遺跡地下 | Ruines B des Sept Étoiles | 七星 elsewhere = Grande Ourse |
| 海賊ヴェルカントの洞くつ | Repaire de pirates | |
| 試練の迷宮 | Epreuve du labyrinthe | |
| 廃坑地下N階 | Mine abandonnée - Niv.N | |
| リヴォースタワー | Tour Rivorse | |
| 宝物殿 | Salle du trésor | |
| オラクルルーム（レベルN） | Antichambre de l'oracle (Nv N) | |
| ライアスの屋敷 | Manoir de Ryas | |
| 地下牢 | Donjon | |
| 〜の家 | Maison de 〜 | |

### Buildings, rooms, time captions

| JP | FR |
|---|---|
| 民家 | Maison |
| 宿屋 | Auberge |
| 酒場 | Bar |
| 道具屋 | Quincaillerie |
| 武器屋 | Armurerie |
| 武具屋 | Magasin d'équipement |
| 食料品店 / 食料店 | Épicerie |
| 食物屋 | Restaurant |
| 雑貨屋 | Magasin général |
| 楽器屋 | Magasin de musique |
| スキルギルド | Guilde des savoirs |
| クリエイターの店 | Magasin de Créateur |
| 行商人 | Marchand Ambulant |
| 駐屯所 | Quartier général |
| 廊下 / 寝室 / 客間 / 書斎 | Couloir / Chambre / Chambre d'amis / Salle d'étude |
| 時は少しだけ流れ・・・ | Un peu plus tard... |
| 数時間後・・・ | Plusieurs heures après... |
| 二日後 | Deux jours plus tard... |
| その日の夜 | Cette nuit-là... |

## Organisations, races, jobs, concepts

| JP | FR | note |
|---|---|---|
| ヒューマン | Humain | |
| フェルプール | Felpurr | |
| レッサーフェルプール | Semi Felpurr | |
| ハイランダー | Montagnard | dialog: "des montagnes", montagnards |
| フェザーフォルク | Peuple Ailé | dialog: pluméen ×9 |
| ムーア | Moore | |
| リカントロープ | Lycanthrope | |
| けんし | Épéiste | job |
| ほうじゅつし | Magic User | job, left in English |
| もんしょうつかい | Heraldry Wizard | job, left in English |
| ぶとうか | Chorégraphe | job |
| エンシャントマスター | Enchanteur | job |
| ねこかくとうか | Karatéchat | job |
| きし | Chevalier | job |
| 真紅の楯 | Bouclier écarlate | |
| トライア | Tri-Ace | |
| 紋章術 | héraldique | |
| 紋章 | emblème | |
| 呪紋 | sort (magie) | |
| 奥義 / 奥義書 | arcane (dialog) / ohgi (descriptions) | |
| 必殺技 | attaque létale / mouvement fatal | |
| 魔物 | monstre | |
| 盗賊 | voleur | |
| ウイルス / 血清 / 石化 | virus / sérum / pétrification | |
| フォル | Fol | currency |
| PrivateAction (badge, `C6:96E7`) | ActionPrivée | town split-up mode; English in the JP game, no dialog names it. Official FR (SO2R): action privée (rejected as literal). Badge fits ≈48 px: QuartLibre, Aparté, Escapade |

### Official French elsewhere in the series

Star Ocean 1 never had an official French release: First Departure (PSP) and First Departure R (Switch/PS4) are
English-only, so the community names (Ratix, Clatos, Portmith, Felpurr, Resonia) clash only with the English remakes
(Roddick, Kratus, Portmis, Fellpool, Lezonia). The Second Story R (2023) is the nearest official French:

| EN | SO2R FR | note |
|---|---|---|
| Private Action | action(s) privée(s) | store copy; one review writes "Actions Personnalisées", "AP" |
| Specialty / Super Specialty | spécialité / super spécialité | community: Savoirs, Dons innés |
| Item Creation | création d'objets (CO) | community: Création d'objet |
| Skill points | PC (points de compétences) | community: PS |
| Earth Federation | la Fédération | |
| Kenny (surname) | Kenni | Ronixs's family |

## Stats and menus

### Stats

| JP | FR long | FR 8x8 short |
|---|---|---|
| HP | PV | PV |
| MP | PM | PM |
| LV | NV | NV |
| EXP | EXP | Exp |
| NEXT | Suivant | Suiv |
| STR | Force | Forc |
| INT | Intelligence | Int |
| AGL | Agilité | Agil |
| CON | Constitution | Cons |
| GUTS | Cran | Cran |
| STM | Endurance | Endu |
| こうげき / こうげきりょく | Attaque | |
| ぼうぎょ | Défense | |
| めいちゅう | Précision | |
| かいひ | Esquive | |
| ぞくせい | Élément | |
| しゅぞく | Race | |
| しょくぎょう | Métier | |
| こうぶつ | Plat préféré | Préfère |
| SP | PS | |
| スキルLV | Savoir NV | |
| とくぎLV | NV Talent | TalentNV |
| しょうひMP | Coût PM | PM Requis |
| TIME | Temps | |
| エンカウント | Combats | |
| NPC | PNJ | |
| MASTER | Maître | |

### Commands and screens

| JP | FR |
|---|---|
| とくぎ / 特技 | Talents / Talent |
| アイテム | Bagage |
| せんじゅつ | Groupe |
| レジスト | Régler (menu16: Config.) |
| そうび / 装備 | Équiper |
| スキル | Savoirs / Savoir |
| ステータス | Statut |
| セーブ | Sauver |
| ロード | Charger |
| さくせん / 作戦 | Stratégie / Tactique |
| いれかえ | Échange |
| たいけい / 隊形 | Formation |
| 店 / みせ | Magasin |
| 名前入力 | Nommer |
| タレント | Dons innés |
| アイテムメニュー | Menu du bagage |
| アイテムクリエーション | Création d'objet |
| きちょうひん | Objets précieux |
| そうびメニュー | Équiper |
| さいきょうそうび | Le plus fort |
| イクイップウイザード / EW | Automatique / Auto |
| ON / OFF | Oui / Non |
| はい / いいえ | Oui / Non |
| よろしいですか？ | D'accord ? |
| （なし） | (Vide) |
| かう / うる / みせをでる | Achat / Vente / Fin |
| せいさん / せいさんご | Faire / Total |
| ハトをつかう / はとをだす | Pigeon / Appeler pigeon |
| もっているかず | Bagage |
| なまえ / ニックネーム | Nom / Surnom |
| けってい（命名） / おわり | Défaut / Fin |
| ひっさつわざのせってい / じゅもんのせってい | Arcanes... / Sorts... |
| ひっさつわざ1 / 2 | Arcane 1 / 2 |
| メッセージスピード（はやい/おそい） | Vit.Message (Rapide/Lente) |
| サウンドしゅつりょく（ステレオ/モノラル/サラウンド） | Réglage Son (Stéréo/Mono/3D) |
| MUSIC / SOUND | Musique / Son |
| キーカスタマイズ | Boutons |
| けってい / キャンセル / メニュー / もくひょう | Sélectionner / Annuler / Menu / Cibler |
| ウインドウカラー / カラーブライト | Couleur / Luminosité |
| しゅぎょうする / しない | Exercice / Pas d'exercice |
| なにもしない / てきからにげる / てきをさがす | Ne rien faire / Fuir ennemi / Chercher ennemi |
| さっきょく / えんそう / さっきょくメニュー | Composer / Jouer / Composition |
| ほそくせつめい（はありません） | Avec / Sans informations |
| データをえらんでください / データがありません | Choix d'un bloc / Vide |
| いれかえがめん | Écran d'échange |
| とくぎしゅうとくど / とくぎべつスキルしゅうとくど | Niveaux de talents / Talent prérequis |
| ダミーアイテム | Objet bidon |

### Equipment slots and categories

| JP | FR |
|---|---|
| ぶき / （武器） | <Arme> / (Arme) |
| からだ / （防具） | <Armure> / (Armure) |
| たて | <Bouclier> |
| あたま | <Casque> |
| あし | <Bottes> |
| そのた1 / そのた2 | <Accessoire> |
| （その他） | (Objets) |

### Formations

| JP | FR |
|---|---|
| リニアモーション | En ligne |
| アストラルシフト | Astral |
| トライシフト1 / 2 | Triangle 1 / 2 |
| フリーファイト | Dispersé (desc: Formation libre) |
| アッパースクウェア | Carré haut |
| アンダースクウェア | Carré bas |
| ダイヤモンドシフト | Losange |

### Strategies (さくせん)

| JP | FR |
|---|---|
| せんじんをきれ | Initiative |
| まあいをとれ | Chacun son tour |
| みかたをまもれ | Protéger ses alliés |
| みずからをまもれ | Se défendre |
| われわれをだいいちに | Priorité absolue |
| せんとうをゆうりに | Avantage |
| ほどよくかんがえて | Prudence |
| じゅもんはつかわずに | Pas de sorts |
| よりょくはのこすな / ちからをつかいきれ | Sans retenue |
| とおくをねらえ | À distance |
| かいふくをじゅうし | Priorité aux soins |
| こうげきをじゅうし | Pas de quartiers |
| ひっさつわざはつかうな | Sans technique |

### Battle messages

| JP | FR |
|---|---|
| ＭＰが足りない | Pas assez de PM |
| はレベルアップ！ | a gagné un niveau |
| を手に入れた！ | a été obtenu! |
| を覚えた！ | a été appris! |
| バックアタック！ | Attaque par derrière! |
| ボースサイドアタック！ | Embuscade! |

## Elements and statuses

| JP 8x8 | JP desc | FR |
|---|---|---|
| ＜ち＞ | 地属性 | Terre |
| ＜みず＞ | 水属性 | Eau |
| ＜ひ＞ | 炎属性 | Feu |
| - | 氷属性 | Glace |
| ＜かみなり＞ | 雷属性 | Foudre |
| ＜かぜ＞ | 風属性 | Vent |
| ＜ひかり＞ | 光属性 | Lumière |
| ＜やみ＞ | 闇属性 | Ombre |
| - | 死属性 | Mort |
| - | 無属性 | Non élémental |
| のぞくせいによわい | | Faible contre |

Spell descriptions use `Attaque/<Élément>.`

| JP | FR | note |
|---|---|---|
| 毒 | poison | |
| 麻痺 | paralysie (verb: paralyser) | |
| 石化 | pétrification | |
| 行動不能 / 戦闘不能 / 気絶 | inconscient (Ranime un allié inconscient) | |
| 異常状態 | - | descriptions left in English |
| ピヨ | - | no FR term, only the Puantotov items |
| 混乱 | perturber | |
| 呪文を封じる | Confine la magie | (Silence) |

Most menu16/battle16 item descriptions are still English: no other established status terms.

## Spells (呪紋)

| JP | FR 8x8 | FR 16x16 | FR desc |
|---|---|---|---|
| ファイアボルト | TraitFeu | TraitFeu | Flamme |
| アイスニードル | Glacier | Glacier | |
| グレイブ | Tombeau | Tombeau | |
| ウインドブレイド | LameVent | LameVent | Brise |
| シャドウボルト | Mazout | Mazout | |
| イラプション | Éruption | Éruption | |
| ブリザード | Blizzard | Blizzard | |
| アースグレイブ | Sismique | Sismique | |
| サンダーボルト | Foudre | Foudre | |
| ウーンズ | Lésions | Lésions | |
| レイ | Rayons | Rayons | |
| トラクタービーム | Traction | Traction | |
| エクスプロード | Pyros | Pyros | |
| Ｓクリスタル | Crist.S. | Crist.S. | |
| アースクェイク | Secousse | Secousse | |
| サンダーストーム | Tempête | Tempête | |
| ワードオブデス | Vaudou | Vaudou | |
| ライトクロス | Lumière | Lumière | |
| プリズミックソル | PrismicS | PrismicS | |
| スターフレア | Météores | Météores | |
| エクステンション | Néant | Néant | |
| グレムリンレアー | Gremlins | Gremlins | |
| メテオスォーム | Astre | Astre | |
| ダークサークル | Macabre | Macabre | |
| ヒール | Santé | Santé | Soin |
| ディープミスト | Poix | Poix | |
| プレス | Presse | Presse | |
| フィクスクラウド | Nuées | Nuées | Gaz moutarde |
| アンチドート | Antidote | Antidote | |
| サイレンス | Silence | Silence | |
| アシッドレイン | Smog | PluieAcide | Pluie acide |
| キュアオール | PolySoin | PolySoin | Mercurochrome |
| グロース | Pousse | Pousse | Croissance |
| キュアライト | Thérapie | Thérapie | |
| プロテクション | Garde+ | Protection | Bouclier |
| ディスペル | Cure | Cure | Dissipation |
| ヘイスト | Hâte | Hâte | |
| ディレイ | Lenteur | Lenteur | |
| フェアリィヒール | UniFéé | UniFéé | Féerie |
| フェアリィライト | PolyFéé | PolyFéé | Enchantement |
| グラビティプレス | Gravité | Gravité | |
| レイズデッド | Lazzarus | Lazzarus | Lazarus |

## Special moves (必殺技 / 奥義)

Recurring vocabulary: 七星 = Grande Ourse (GO), 蒼龍/蒼竜 = dragon azur (DA), 黒竜 = dragon noir, 緋竜 = dragon rouge,
朱雀 = oiseau vermillon (OV), 玄武 = tortue noire, 白虎 = tigre blanc, 紅蓮 = vermeil, 閃光 = flash, 雷鳴 = éclair,
疾風 = rafale, 旋風 = cyclone, 棍 = bâton, 招来 = invocation, 桜花 = sakura, 八卦掌 = Baguazhang, 気功 = Qigong.

| JP | FR 8x8 | FR 16x16 | FR desc |
|---|---|---|---|
| 双破斬 | D.Tranche | Double tranche | Double tranchant |
| 空破斬 | C.Aérien | Air Slash | Rafale |
| 衝裂破 | C.Fente | Contre fente | |
| 衝霊破 | B.Mental | Boutoir mental | |
| 雷鳴剣 | É.Éclair | Épée éclair | |
| 紅蓮剣 | É.Vermeil | Épée vermeil | |
| 閃光剣 | É.Flash | Épée flash | |
| 蒼龍醒雷斬 | L.FoudrDA | Lame de foudre du dragon azur | Dragon de foudre |
| 朱雀翔撃破 (剣) | VictoirOV | Victoire de l'oiseau vermillon | Souffle du moineau |
| 七星雷鳴剣 | É.Écl.GO | Épée éclair de la Grande Ourse | |
| 七星閃光剣 | É.FlashGO | Épée flash de la Grande Ourse | |
| 七星双破斬 | D.TranGO | Double tranche de la Grande Ourse | Double lame de la Grande Ourse |
| 七星紅蓮剣 | É.Verm.GO | Épée vermeil de la Grande Ourse | |
| 双流戟破 | D.Estoc | - | Double estoc |
| 襲爪戟破 | D.C.B. | - | Griffe de dragon |
| 星天衝 | T.Météor | - | Météore |
| 吼竜破 | Fureur D. | Fureur du dragon | |
| 黒竜天雷破 | FoudresDN | Foudres du dragon noir | |
| 緋竜天雷破 | FoudresDR | Foudres du dragon rouge | |
| 蒼龍天雷破 | FoudresDA | Foudres du dragon azur | |
| 七星招雷破 | - | Foudres de la Grande ourse | |
| 訃虎招来 | - | Apparition du tigre | |
| 蒼龍招来 | InvDragon | Invocation du dragon azur | |
| 玄武招来 | InvTortue | Invocation de la tortue noire | Invocation du guerrier sombre |
| 白虎招来 | InvTigre | Invocation du tigre blanc | |
| レイヴンソード | É.Corbeau | Épée du corbeau | |
| ダンシングソード | É.Dansant | Dancing Sword | Lame dansante |
| 3VOLLEY | 3 Volées | 3 volées | |
| 3WAY | 3 Sens | 3 sens | Triple orientation |
| アクアスプレッド | DiffusEau | Diffusion d'eaud (sic) | Jet d'eau |
| ギャラクシィゴッドブレス | SouffleDG | Souffle du dieu de la Galaxie | |
| シルヴァンショット | JetSylvan | Jet Sylvanien | |
| アンホーリィテラー | T.Impie | Terreur impie | |
| ヴィクトリーテラー | T.Vict. | Terreur victorieuse | |
| 気功掌 | PaumeQig. | Paume Qigong | |
| 流星掌 | PaumeMété | Paume météore | Poing météore |
| 練気拳 | P.Psych | Poing psychique | |
| 気功蹴 | Pd.Qigong | Coup de pied Qigong | |
| 蒼龍醒雷破 | Tonnerre | Tonnerre du dragon azur | |
| 玄武覇王拳 | Emprise | Emprise de la tortue noire | |
| 白虎吼破弾 | Blâmes | Blâmes du tigre blanc | |
| 朱雀翔撃破 (拳) | Triomphe | Triomphe de l'oiseau vermillon | Souffle du moineau |
| 桜花八卦掌 | BGZhSaku | Baguazhang du sakura | Coup du cerisier |
| 裏桜花炸光 | Éc.Sakura | Éclat retourné du sakura | Éclat inversé du cerisier |
| 旋風棍 | B.Cyclone | Bâton cyclone | |
| 紅蓮旋風棍 | B.Cyc.Ver | Bâton cyclone vermeil | |
| 疾風棍 | B.Rafale | Bâton rafale | |
| 疾風破裏拳 | B.Raf.Mut | Bâton rafale mutilateur | Bâton rafale mutileur |
| 覇王疾風棍 | B.Raf.Tyr | Bâton rafale tyran | |
| 霧氷凍棍 | B.Frimas | Bâton frimas | |
| 武神飛翔棍 | B.VolantH | - | (Réservé) |
| 水月両断破 | Coupure R | Coupure de reflet | Tranche miroir |
| 伸破無頼棍 | E.R.S. | - | (Réservé) |
| 七星乱舞 | BringueGO | Bringue de la Grande Ourse | Vacarme de la Grande Ourse |
| レイヴンオーブ | O.Corbeau | Orbe du corbeau | |
| フレアオーブ | O.Incand | Orbe incandescente | |
| ヘイルオーブ | O.Grêle | Orbe de grêle | |
| サンダーオーブ | O.Foudre | Orbe de foudre | |
| アーククリスタル | Arche Cr. | Arche de cristal | |
| シールクリスタル | Cr.Sceau | Cristal-sceau | Cristal de soie |
| サザンクロス | CroixSud | Croix du sud | |
| セブンス・スター | 7 Étoiles | 7 Étoiles | Grande Ourse |
| ギャラクシィ | Galaxie | Galaxie | |
| デスクリスタル | CristMort | Cristal de la Mort | |
| シャイニングダンス | D.Brillan | Danse de lumière | Danse brillante |
| プリズミックダンス | D.Prismiq | Danse prismique | Danse prismatique |
| マジカルダンス | D.Magique | Danse magique | |
| マルチプルぱんち | Mlt.Poing | Multipoing | |
| スプレッドみそ / ミサイル | M.Propag | Missile à propagation | |
| ねりちゃぎっ♪ | C.P.Hache | Coup de pied hache | Coup de pied sauté |
| えいっ！やぁ！とぉ！♪ | 1!2!3! | Une ! Deux ! Trois ! | |
| JP・P・Cサマーソルト | Galipette | S.P., P. Galipette C | |
| パニックダンス | D.Panique | Danse Panique | |
| チャーミングポーズ | D.Charme | Danse Charmeuse | |
| ドリームコンボ | ComboRêve | Combo de rêve | |
| そらをみろ♪ | Le Ciel | Regarde le ciel | Aaah! |

## Skills (スキル, FR « Savoirs »)

| JP | FR | note |
|---|---|---|
| せいぶつがく | Biologie | |
| やくそうがく | Botanique | |
| せいしんがく | Psychologie | |
| こうぶつがく | Minéralogie | |
| どうぐちしき | Outils | |
| ピエティ | Piété | desc: Théologie |
| レシピ | Cordon bleu | |
| オタマジャクシ | Solfège | |
| ようせいろん | Folklore | |
| びてきかんかく | S.Esthét. | |
| めきき | Expert | |
| きのうび | Efficacité | |
| あそびごころ | S.Humour | |
| きけんかんち | S.Danger | |
| でんぱ | Ondes R. | |
| どりょく | Obstin. | |
| こんじょう | Persévérance | |
| にんたい | Stoïcisme | |
| クラフト | Doigté | |
| ほうちょう | Couteau | |
| えんそう | Interprétation | |
| くちぶえ | Siffler | |
| デッサン | Dessin | |
| ぶんぴつ | Écriture | |
| キャスト | Moulage | |
| かがくぎじゅつ | Technos | dialog: Technoscience |
| ダッシュ | Marathon | |
| ちょうきょう | Domptage | |
| しょうげきは | OndeChoc | |
| しんくうは | ImpactA. | desc: Impact aérien |
| めくり | VolteFace | |
| はんげき | Riposte | |
| フェイント | Feinte | |
| れんき | Concentrer | |
| リンクコンボ | Combos | |
| はやくち | Prolixe | |
| レイヴンソード / レイヴンオーブ | É.Corbeau / O.Corbeau | |
| かくとうじゅつ | Bagarre | |
| エダールけんぎ | Edarl | |
| がりゅうけん | Autodid. | |
| ねこかくとう | Charaté | |
| しちせいおうぎ | G.Ourse | |
| しせいじゅう | 4Animaux | desc: 4 bêtes sacrées |
| こうりゅうおうぎ | Dragon | desc: dieu Dragon |
| ぶしんおうぎ | Hachiman | dialog: dieu guerrier |
| はっけしょう | Baguazhang | |
| うらおうか | Sakura | desc: Dessous de cerisier |
| ネコおうぎ♪ | Chat<Note> | |
| もんしょう | Blasons | |
| じゃんく | Déchets | |
| ラプスそうぎほう | Raps | |

Categories (menu16): 戦闘スキル, 流派スキル (dialog: savoir de Style), 奥義スキル (ohgi).

### Item creation specialties (アイテムクリエーション)

| JP | FR 8x8 | note |
|---|---|---|
| さいく / 細工 | Orfèvre | |
| ちょうり / 調理 | Cuistot | |
| ちょうごう / 調合 | Mixeur | |
| かんてい / 鑑定 | Expert | menu16: Savant |
| カスタマイズ | Ajusteur | |
| アート | Artiste | |
| しっぴつ / 執筆 | Auteur | |
| おんがく / 音楽 | Musicien | |
| しゅぎょう / 修行 | Bosseur | menu16: Entraînement |
| れんきん / 錬金 | Chimiste | |
| オラクル | Oracle | |
| かたなかじ / 刀鍛冶 | Forgeron | |
| ダッシュ | Coureur | |
| ファミリア | Oiselier | |
| スカウト | Pisteur | |
| エンチャント | Envoûter | |
| しゅうり / 修理 | Rétameur | |

### Talents (タレント, FR « Dons innés »)

| JP | FR |
|---|---|
| オリジナリティ | Originalité |
| みかく | Bon goût |
| きようなゆびさき | Doigts de fée |
| デザインセンス | Esthétisme |
| ぶんさい | Talent littéraire |
| リズムかん | Sens du rythme |
| おんかん | Oreille musicale |
| どうぶつずき | Amour des animaux |
| やせいのかん | Instinct |
| マナのしゅくふく | Bénédiction de mana |

## Items

Families: ソード → `Épée …`, リング → `Bague …`, ヘルム → `Casque …`, グリーブ → `Grèves …`, シールド → `Écu …`,
ガード → `Garde …`, ブーツ → `Bottes …`, ボウ → `Arc …`, ローブ → `Robe …`, スーツ → `Tenue …`, アイドル → `Idole …`,
チェック → `Torque …`, シンボル → `Signe …`, ぞう → `Statue …`, しょうぞうがA–L → `Portrait A–L`, ドワーヴン → `nain(e)`,
エルヴン → `elfique`, シルヴァン → `sylvain(e)`, ホーリィ → `béni(e)`, ねこ → `chat`, ミスリル → `mithril`, ごうかな → `… de luxe`,
ミラージュ → `… mirage`. Japanese sake names kept in romaji (Ichinokura, Senchû, Yaegaki Mu, Tamano, Bijôbu, Koku Ryû).

### Descriptions

Item id X: name `names8[X]`, battle help `battle16[X]` (one line, ≤ 180 px: the Japanese is at most 15 full-width
characters), menu description `menu16[X + 0xEA61]` (the item panel: the name line, then at most 2 lines of 224 px,
wrapped at spaces by the VWF). Widths: dialog font advance + 1 px (`tools/menu_font16.py`).

- Translate from the Japanese; the old English is a hint only.
- Battle help: terse, no article, no final period, as the Japanese (`ＨＰ回復` → `Restaure les PV`).
- Menu description: full sentences, final period. Category openers as the old team: `薬草の一種` → `Une plante.`,
  `食材の一種` → `Ingrédient.`; unidentified: `Ça ressemble à …, mais sans l'identifier, impossible d'en savoir plus.`
- Stats and statuses as in *Stats* and *Elements and statuses* (`PV`, `PM`, poison, paralysie, pétrification); skills by
  their *Skills* names; other items by their FR 8x8 name.
- Effects: `回復` → `restaure` (PV/PM) / `soigne` (status); `行動不能から回復` → `ranime`; `味方1人` / `味方全員` → `un allié` /
  `tous les alliés`; `敵1体` / `敵全体` → `un ennemi` / `tous les ennemis`.

### Full list

| id | JP | FR 8x8 |
|---|---|---|
| 1388 | マンドレイク | Mandragore |
| 1389 | セボリー | Sauge |
| 138A | アルテミスリーフ | Anthémis |
| 138B | シャドゥフラウア | Sarracenia |
| 138C | ラベンダー | Lavande |
| 138D | マジックカード | Magicarte |
| 138E | マジックカラー | Magichrome |
| 138F | リサーチペン | Stylo d'étude |
| 1390 | クリエイターペン | Stylo créatif |
| 1391 | スミスハンマー | Marteau forge |
| 1392 | ミックスハンマー | Marteau mixte |
| 1393 | スペクタクルズ | Bésicles |
| 1394 | ダマスクス | Damas |
| 1395 | ミスリル | Mithril |
| 1396 | オリハルコン | Orichalque |
| 1397 | ルーンメタル | Métal runique |
| 1398 | ムーナイト | Sélénite |
| 1399 | ミーティアライト | Météorite |
| 139A | けんじゃのいし | Alkahest |
| 139B | ルビー | Rubis |
| 139C | スタールビー | Rubis étoilé |
| 139D | サファイア | Saphir |
| 139E | グリーンベリル | Béryl vert |
| 139F | クリスタル | Cristal |
| 13A0 | ダイヤモンド | Diamant |
| 13A1 | レインボーダイヤ | Iridiamant |
| 13A2 | シルバー | Argent |
| 13A3 | ゴールド | Or |
| 13A4 | アイアン | Fer |
| 13A5 | トランペット | Trompette |
| 13A6 | クラリネット | Clarinette |
| 13A7 | ハーモニカ | Harmonica |
| 13A8 | しゃみせん | Shamisen |
| 13A9 | ギター | Guitare |
| 13AA | トロンボーン | Trombone |
| 13AB | バイオリン | Violon |
| 13AC | サックス | Saxophone |
| 13AD | こくもつ | Céréales |
| 13AE | くだもの | Fruits |
| 13AF | やさい | Légumes |
| 13B0 | にくるい | Viande |
| 13B1 | ぎょかいるい | Fruits de mer |
| 13B2-13CA (×25) | ？WEAPON | ?Arme |
| 13CB-13D9 (×15) | ？GUARD | ?Défense |
| 13DA-13E8 (×15) | ？ITEM | ?Réserve |
| 13E9-13EF (×7) | ？JEM | ?Gemme |
| 13F0-13F9 (×10) | ？JEWELRY | ?Bijou |
| 13FA-13FE (×5) | ？HERB | ?Herbe |
| 13FF | ？FOOD | ?Vivres |
| 1400-1405 (×6) | ？FOOD | ?Vivres |
| 1406 | バブルポーション | Bullixir |
| 1407 | メルトポーション | Fusixir |
| 1408 | スティンクポット | Shlinguixir |
| 1409 | ビターポーション | Âcrixir |
| 140A | フルーツポット | Fruitixir |
| 140B | フレッシュボトル | Ravigotant |
| 140C | ポイズンボム | Toxotov |
| 140D | キラーポイズン | Toxotov+ |
| 140E | スイートポット | Sucrixir |
| 140F | リキュールボトル | Liqueur |
| 1410 | スイートシロップ | Sirop doux |
| 1411 | サワーシロップ | Sirop aigre |
| 1412 | ミックスシロップ | Sirop mixte |
| 1413 | ホーリィミスト | Brume bénie |
| 1414 | スティンクボム | Puantotov |
| 1415 | ピコピヨボム | Puantotov+ |
| 1416 | フェアリィグラス | Féérixir |
| 1417 | フェアリィミスト | Brume de fée |
| 1418 | マインドボム | Psychotov |
| 1419 | ギガマインドボム | Psychotov+ |
| 141A | リザレクトミスト | Brume de vie |
| 141B | リザレクトボトル | Fiole de vie |
| 141C | フレアボム | Flambotov |
| 141D | メガフレアボム | Flambotov+ |
| 141E | キュアポイズン | Antipoison |
| 141F | キュアパラライズ | Antiparalysie |
| 1420 | キュアストーン | Antipierre |
| 1421 | ウィッチパウダー | Limpinpine |
| 1422 | エルヴンパウダー | Elfinine |
| 1423 | シンデレラグラス | Cendrillon |
| 1424-157D (×24) |  |  |
| 1425 | ウィルポーション | Volontixir |
| 1426 | マイトポーション | Couragixir |
| 1427 | スペルポーション | Magixir |
| 1429 | フレアリング | Bague flamme |
| 142A | バーサークリング | Bague furie |
| 142B | アクアリング | Bague aqua |
| 142C | ピヨハン | Piyohan |
| 142D | エメラルドリング | Bague béryl |
| 142E | フェアリィリング | Bague fée |
| 142F | ルナテックリング | Bague lunaire |
| 1430 | スターリング | Bague étoile |
| 1431 | メンタルリング | Bague mentale |
| 1432 | レジストリング | Bague parade |
| 1433 | リフレクトリング | Bague reflet |
| 1434 | ヒールリング | Bague soin |
| 1435 | シールドリング | Bague bouclier |
| 1436 | プロテクトリング | Bague égide |
| 1437 | レビテートリング | Bague envol |
| 1438 | シルバーリング | Bague d'argent |
| 1439 | ゴールドリング | Bague d'or |
| 143A | ブローチ | Broche |
| 143B | ゴールドブローチ | Broche d'or |
| 143C | プリティアイドル | Jolie idole |
| 143D | ルビーペルシャ | Persan rubis |
| 143E | ネックレス | Collier |
| 143F | クラウン | Couronne |
| 1440 | カエル | Grenouille |
| 1441 | マジカルペルシャ | Persan magique |
| 1442 | シルバーアイドル | Idole d'argent |
| 1443 | ゴールドアイドル | Idole d'or |
| 1444 | タリスマン | Talisman |
| 1445 | ルナタリスマン | Talisman lunaire |
| 1446 | ルナタブレット | Tablette lunaire |
| 1447 | スターネックレス | Collier étoile |
| 1448 | スタークレスト | Blason étoile |
| 1449 | フィートシンボル | Signe totem |
| 144A | ミスティシンボル | Signe brumeux |
| 144B | ポイズンチェック | Torque poison |
| 144C | パラライチェック | Torque stase |
| 144D | ストーンチェック | Torque pierre |
| 144E | パープルミスト | Brume mauve |
| 144F | マジックミスト | Brume magique |
| 1450 | リバースドール | Retounaît |
| 1451 | マジカルドロップ | Goutte magique |
| 1452 | ドリームクラウン | Tiare Rêve |
| 1453 | シルバーアンク | Ankh d'argent |
| 1454 | ぶさいくなゆびわ | Bague moche |
| 1455 | へんなにんぎょう | Poupée bizarre |
| 1456 | センスないゆびわ | Bague ringarde |
| 1457 | へっぽこなかざり | Bijou kitsch |
| 1458 | へんなかたまり | Machin |
| 1459 | はずかしいかざり | Bijou gênant |
| 145A | わらえるかたまり | Truc risible |
| 145B | せいぶつりろん | Biologie |
| 145C | やくそうずかん | Herbier |
| 145D | せいしんがくろん | Psychologie |
| 145E | たのしいこうぶつ | Minéralogie |
| 145F | どうぐずかん | Les outils |
| 1460 | おりょうりずかん | La cuisine |
| 1461 | がくてん | Mélomania |
| 1462 | しんぴのようせい | Fée mystique |
| 1463 | しょくざいえらび | Cordon bleu |
| 1464 | ドワーフぎじゅつ | L'art nain |
| 1465 | しょくにんごころ | Artisanat |
| 1466 | バイエル | AB-Musique |
| 1467 | えごころのすべて | L'esprit de l'art |
| 1468 | ぶんぽうろん | Bled |
| 1469 | ぶきのすべて | Les armes |
| 146A | ヘルメスのりろん | Hermès |
| 146B-1470 (×6) | よげんしょ | Prophéties |
| 1471-1475 (×3) | どーじん | FanArt |
| 1473 | どーじん | Hentai |
| 1474 | どーじん | DC Comics |
| 1476 | フルーツパフェ | Parfait |
| 1477 | アップルパイ | Tarte Tatin |
| 1478 | シャーベット | Sorbet |
| 1479 | オレンジシェイク | Lait orange |
| 147A | フルーツケーキ | Cake |
| 147B | ワイン | Vin |
| 147C | シチュー | Ragoût |
| 147D | サラダ | Salade |
| 147E | ロールキャベツ | Chou farci |
| 147F | ホイコーロー | Hui guo rou |
| 1480 | せんそうゼリー | Jell-O |
| 1481 | まつたけボイル | Matsutake |
| 1482 | ステーキ130 | Steak-130g |
| 1483 | ステーキ240 | Steak-240g |
| 1484 | ぢどりくしやき | Brochette |
| 1485 | ユッケジャン | Yukgaejang |
| 1486 | ハンバーグ | Hamburger |
| 1487 | エスカルゴ | Escargot |
| 1488 | とろ | Thon |
| 1489 | おおとろ | Thon gras |
| 148A | えびフライ | Crevette |
| 148B | たいさし | Sashimi |
| 148C | サザエつぼやき | Bulot |
| 148D | シーフードスパ | Spaghetti |
| 148E | いちのくら | Ichinokura |
| 148F | せんちゅう | Senchû |
| 1490 | やえがき”む” | Yaegaki Mu |
| 1491 | たまのひかり | Tamano |
| 1492 | びじょうぶ | Bijôbu |
| 1493 | こくりゅう | Koku Ryû |
| 1494 | シーフォンチュー | Xifeng Jiu |
| 1495 | さんぞうしゅ | Bibine |
| 1496 | やすいさしみ | Poiscaille |
| 1497 | まずいシチュー | Tambouille |
| 1498 | かたいステーキ | Semelle |
| 1499 | まずいデザート | Dessert raté |
| 149A | からいケーキ | Gâteau épicé |
| 149B | VICTORY | Victoire |
| 149C | CRITICAL | Critique |
| 149D | PHOENIX | Phénix |
| 149E | TREASURE | Trésor |
| 149F | UPSTART | Avide |
| 14A0 | はやぶさのぞう | Statue faucon |
| 14A1 | ししのぞう | Statue lion |
| 14A2 | あくまのぞう | Statue démon |
| 14A3 | どくろのぞう | Statue crâne |
| 14A4 | しょうぞうがA | Portrait A |
| 14A5 | しょうぞうがB | Portrait B |
| 14A6 | しょうぞうがC | Portrait C |
| 14A7 | しょうぞうがD | Portrait D |
| 14A8 | しょうぞうがE | Portrait E |
| 14A9 | しょうぞうがF | Portrait F |
| 14AA | しょうぞうがG | Portrait G |
| 14AB | しょうぞうがH | Portrait H |
| 14AC | しょうぞうがI | Portrait I |
| 14AD | しょうぞうがJ | Portrait J |
| 14AE | しょうぞうがK | Portrait K |
| 14AF | しょうぞうがL | Portrait L |
| 14B0-14B1 (×2) | らくがき | Croûte |
| 14B2 | せんしのつぼ | Vase guerrier |
| 14B3 | もんしょうのつぼ | Vase armorié |
| 14B4 | マジカルジャー | Jarre magique |
| 14B5 | サンタブーツ | Bottes de Noël |
| 14B6 | ブルーベリィ | Myrtille |
| 14B7 | ブラックベリィ | Mûre |
| 14B8 | アクアベリィ | Aiguebaie |
| 14BB | ストラングソード | Épée ficelée |
| 14BC | マーヴェルソード | Épée inouïe |
| 14BD | メテオクラッシュ | Météocrash |
| 14BE | ムーンファルクス | Falx Lune |
| 14BF | ソウルイーター | BuveuseÂme |
| 14C0 | スティルソード | Empêtreuse |
| 14C1 | ミスリルソード | Épée mithril |
| 14C2 | シルヴァンス | Sylvance |
| 14C3 | ダマスクスソード | Épée damas |
| 14C4 | ドワーヴンソード | Épée naine |
| 14C5 | エアスラッシュ | Lame de vent |
| 14C6 | ホーリィソード | Épée bénie |
| 14C7 | デュエルソード | Épée de duel |
| 14C9 | アストラルソード | Épée astrale |
| 14CA | エレメントソード | Élémentale |
| 14CB | イグニートソード | Épée ardente |
| 14CC | バハムートティア | Larme Bahamut |
| 14CD | グローサルソード | Crescendo |
| 14CE | ガンブレイド | Pistolame |
| 14CF | シルバーソード | Épée d'argent |
| 14D0 | メテオストライク | Météochoc |
| 14D1 | スレイヤーソード | Dévoreuse |
| 14D2 | ドゥームブレイド | Jugeresse |
| 14D3 | ヴォーパルソード | Épée vorpale |
| 14D4 | ベルセルクソード | Épée berserk |
| 14D5 | クラックブレード | Lame fêlée |
| 14D6 | CSSS | É.S.S.C. |
| 14D7 | アサシンダガー | Poignard |
| 14D8 | フレアバゼラード | Poignard |
| 14D9 | ブラッディソード | Épée sanglante |
| 14DA | アイスコフィン | Écrin glacé |
| 14DB | エレメントエッジ | Fil élémentaire |
| 14DC | ドラゴンエッジ | Fil du dragon |
| 14DD | ラウンデルダガー | Dague rondelle |
| 14DE | フェイムフェイス | Fameface |
| 14DF | メタルファング | Croc de métal |
| 14E0 | ブレイズナックル | Pyropoing |
| 14E1 | ペインセスタス | Ceste douleur |
| 14E2 | ドラゴンクロウ | Serre dragon |
| 14E3 | ネコファング♪ | Croc chat♪ |
| 14E5 | セントハルバード | Hallebénie |
| 14E6 | スピニングスピア | Rotolance |
| 14E7 | メックハルバード | Halleméca |
| 14E8 | ドラゴンランス | Lance dragon |
| 14E9 | フレイムランサー | Boutefeu |
| 14EA | フレアスプレッド | Arc flambant |
| 14EB | シルヴァンボウ | Arc sylvain |
| 14EC | エルヴンボウ | Arc elfique |
| 14ED | ライトニングボウ | Arc éclair |
| 14EE | ラピッドボウ | Arc rapide |
| 14F0 | オーラブレード | Lame d'aura |
| 14F1 | アークウィンド | Arc du vent |
| 14F2 | シウススペシャル | Spécial Cius |
| 14F3 | ムラサマブレード | Muramasa |
| 14F4 | おまもり | Amulette |
| 14F5 | カイザーナックル | Poing Kaiser |
| 14F6 | デスブリンガー | Fatalité |
| 14F7 | ホーリィオーブ | Orbe béni |
| 14F8 | ほうてんげき | Bi-Lame |
| 14F9 | Qきょくパンチ♪ | Pugilat Q♪ |
| 14FA | なまくらソード | Épée émoussée |
| 14FB | ガラクタ | Déchets |
| 14FD | ロングソード | Épée longue |
| 14FE | サーベル | Sabre |
| 14FF | シンクレアー | Sinclair |
| 1500 | ワルーンソード | Épée wallonne |
| 1501 | トゥハンドソード | Montante |
| 1502 | クレイモア | Claymore |
| 1503 | ツヴァイハンダー | Espadon |
| 1504 | フランヴェルジュ | Flamberge |
| 1505 | スモールソード | Épée courte |
| 1506 | グラディウス | Glaive |
| 1507 | バゼラード | Baselard |
| 1508 | ロッド | Bâton |
| 1509 | ルビーワンド | Sceptre rubis |
| 150A | クレストロッド | Crosse |
| 150B | ナックル | Poing |
| 150C | ハードナックル | Poing dur |
| 150D | ハグナク | Bagh nakh |
| 150E | セスタス | Ceste |
| 150F | こん | Bâton |
| 1510 | スピア | Lance |
| 1511 | ロングスピア | Pique |
| 1512 | ハルバード | Hallebarde |
| 1513 | さんせつこん | Nunchaku |
| 1514 | ショートボウ | Arc court |
| 1515 | ロングボウ | Arc long |
| 1516 | クロスボウ | Arbalète |
| 1517 | アルヴァレスト | Cranequin |
| 1519 | レザーアーマー | Armure de cuir |
| 151A | バンデッドメイル | Armure laminée |
| 151B | リングメイル | Jaseran |
| 151C | ブリガンディ | Brigandine |
| 151D | プレートメイル | Lamellaire |
| 151E | スチールアーマー | Armure d'acier |
| 151F | ローブ | Robe |
| 1520 | シルクローブ | Robe de soie |
| 1521 | アンバーローブ | Robe d'ambre |
| 1522 | シルバーローブ | Robe d'argent |
| 1523 | ホーリィクローク | Scapulaire |
| 1524 | ぶどうぎ | Keikogi |
| 1525 | チャイナどうぎ | Gi chinois |
| 1526 | ちゅうかどうぎ | Gi Qin |
| 1527 | バトルスーツ | Tenue combat |
| 1528 | そまつなビキニ | Bikini simple |
| 1529 | ビキニ | Bikini |
| 152A | プリティビキニ | Bikimimi |
| 152B | ねこスーツ | Tenue de chat |
| 152C | レザーヘルム | Casque de cuir |
| 152D | バンデッドヘルム | Casque laminé |
| 152E | アイアンヘルム | Casque de fer |
| 152F | プレートヘルム | Armet |
| 1530 | スチールヘルム | Casque d'acier |
| 1531 | ウッドシールド | Targe en bois |
| 1532 | ラウンドシールド | Rondache |
| 1533 | ナイツシールド | Écu chevalier |
| 1534 | ファインシールド | Écu fin |
| 1535 | レザーグリーブ | Grèves de cuir |
| 1536 | アイアングリーブ | Grèves de fer |
| 1537 | プレートグリーブ | Grèves plaques |
| 1538 | シルバーグリーブ | Grèves d'argent |
| 1539 | ブーツ | Bottes |
| 153A | スエードブーツ | Bottes daim |
| 153B | レザーブーツ | Bottes cuir |
| 153C | サンダル | Sandales |
| 153D | ぶどうシューズ | Tsuranuki |
| 153E | チャイナシューズ | Souliers chinois |
| 153F | ちゅうかシューズ | Souliers Qin |
| 1540 | ドワーヴンメイル | Cotte naine |
| 1541 | リフレックス | Reflex |
| 1542 | ミスリルメッシュ | Mithriline |
| 1543 | シルヴァンメイル | Cotte sylvaine |
| 1544 | デュエルスーツ | Tenue de duel |
| 1545 | マジカルビキニ | Magikini |
| 1546 | ねこアーマー | Armure de chat |
| 1548 | ドワーヴンヘルム | Casque nain |
| 1549 | ミスリルヘルム | Casque mithril |
| 154A | シルヴァンヘルム | Casque sylvain |
| 154B | ハーミットヘルム | Casque ermite |
| 154C | デュエルヘルム | Salade de duel |
| 154D | ねこバンド | Bandeau chat |
| 154E | エルヴンキャップ | Coiffe elfique |
| 1550 | ドワーヴンブーツ | Bottes naines |
| 1551 | エルヴンブーツ | Bottes elfiques |
| 1552 | ミスリルグリーブ | Grèves mithril |
| 1553 | シルヴァンブーツ | Bottes de sylve |
| 155A | アンクシールド | Écu ankh |
| 155B | ドワーヴンガード | Garde naine |
| 155C | ミスリルシールド | Écu mithril |
| 155D | シルヴァンガード | Garde sylvaine |
| 155E | スターガード | Garde étoile |
| 1563 | レイブンオーブ | Orbe corbeau |
| 1564 | アストラルリング | Bague astrale |
| 1565 | フェザーリング | Bague plume |
| 1567 | ロングソード＋1 | Épée longue+1 |
| 1568 | ロングソード＋2 | Épée longue+2 |
| 1569 | クレイモア＋1 | Claymore+1 |
| 156A | クレイモア＋2 | Claymore+2 |
| 156B | グラディウス＋1 | Glaive+1 |
| 156C | グラディウス＋2 | Glaive+2 |
| 156D | ナックル＋1 | Poing+1 |
| 156E | ナックル＋2 | Poing+2 |
| 156F | ロングスピア＋1 | Pique+1 |
| 1570 | ロングスピア＋2 | Pique+2 |
| 1571 | シルバーナックル | Poing d'argent |
| 1572 | ワールウィンド | Tourbillon |
| 1573 | ハトのえさ | Graines |
| 1574 | いしころ | Caillou |
| 1575 | ごうかなけん | Épée de luxe |
| 1576 | ごうかなよろい | Armure de luxe |
| 1577 | ごうかなつえ | Bâton de luxe |
| 1578 | ごうかなローブ | Robe de luxe |
| 1579 | ミラージュマント | Cape mirage |
| 157A | ミラージュローブ | Robe mirage |
| 157B | スタークローク | Cape étoilée |
| 157E | つるはし | Pioche |
| 157F | バニーホイッスル | Sifflet lapin |
| 1580 | フォースソード | Épée de force |
| 1581 | はっけおうぎしょ | Parchemin |
| 1582 | おムスビ | Onigiri |
| 1583 | セントエルモ | Saint-Elme |
| 1584 | オカリナ | Ocarina |
| 1585 | ひうちいし | Silex |
| 1586 | トライエンブレム | Tri-emblème |

### Key items (きちょうひん)

| JP | FR |
|---|---|
| つうこうしょう | Passe |
| ヴァンエンブレム | E.Van (desc: Emblème de Van) |
| シルバエンブレム | E.Sylval |
| ムーアエンブレム | E.Moore |
| アストエンブレム | E.Astral |
| エルダーキー | Clé Aîné |
| セキュリティーR / B | SécuritéR / SécuritéB |
| しんじつのひとみ | ŒilVérité |

## Enemies

| JP | FR |
|---|---|
| とうぞく | Voleur |
| おやぶんベアード | Chef Baird |
| フエルウォーム / ブラッドウォーム / サンドウォーム | Ver Cruel / Ver Pourpre / Shai-Hulud |
| ヴォーパルバニー / リトルバニー / プリティバニー | Lapin Vorpal / Lapinet / Lapinou |
| サーベルバニー / キラー・ラビ / クニークルス | Lapin Rasoir / Lapin Tueur / Cuniculus |
| マンドレイク | Mandragore |
| ホーンドウルフ / ダイアウルフ | Lupuscanis / Lupus |
| スライム / ブラックスライム | Gluant / Gluant Total |
| フッド / ファットフッド | Pudding / Pudding Noir |
| ウルフシェイプ / メールシェイプ | SpectroLupus / SpectroCotte |
| ハウンド/ジャガー/テイパー/フラック/デュエル/ネクロシェイプ | Molossoïde / Jaguaroïde / Tapiroïde / Floconoïde / Schizoïde / Nécroïde |
| ルインガーダー | Gardien des ruines |
| ダースウィドゥ | Maïtïka |
| DARKEYE？ | Sauron |
| メデューサアイ / ドラゴンアイ / デーモニックアイ | Œil de Méduse / Œil de Dragon / Œil Démoniaque |
| チンケシーフ | Arsène |
| カンニバル | Hannibal |
| レッサーアサシン | Aprenti-tueur |
| バーグラー / ブッシュワーカー / ルーター | Cambrioleur / Maquisard / Pillard |
| リザードアクス / ドゥームアクス | Hache Squama / Hache du Jugement |
| プリティベル | Tinterelle |
| グリムフローラ / シャドウフラウア | Flore Sinistre / Fleur Fantôme |
| クラウドオーガ | Ogre Vaporeux |
| パイルビースト / シャドウビースト | Bête de feu / Bête des Ombres |
| グレイヴビット | Morsuvole |
| ヒルジャイアント / ガルガンチュア | Géant des Collines / Gargantua |
| フロードシェリー / パイルシェリー | Chérie Glace / Chérie Feu |
| エルダーマギウス | Archimagius |
| エンジェルナイト / スターセラフ | Séraphine / Séraphin Céleste |
| イーブルテラト / アルクメーネ | Tarentule / Arachno |
| ダークストーカー | Vampiren |
| レディ・エルビス | Dame Elvire |
| プチデビル / スペンドデビル | Minions / Diable à Pointes |
| ゲレル / ペトロゲレル | Grell / Pétrogrell |
| オティフ | Otyugh |
| アラコッラ | Aarakocra |
| ヨチョール | Yochlol |
| スティージ | Stygie |
| プロトアスピテル / アスピテルMK2 / MK3 | Aspitel V1 / V2 / V3 |
| ダーク・ロウ | Loi de Mort |
| アンホーリィエル | Impie |
| カルライーグル | Aigle Carlin |
| デスチャロナ | Charona Mortelle |
| ドロウレクター | Copiste |
| ラプターキング | Roi Raptor |
| ジャンブリン | Jean Bryn |
| リュシオル | Luciole |
| ペリュトン | Péryton |
| クレリック / ラルヴァ | Larve / Larve |

## Inconsistencies

| JP | FR variants (source ×N) |
|---|---|
| ミリー | Milly (8x8, dialog ×244) / Millie (names8 full ×1) |
| ルーン (8x8 `$000D`) | Dorn, should be Rune |
| ジエ | Jay (dialog: speaker ×15, 20 messages) / Jie Revorse (names8) |
| ヴェルカント | Velcant (speaker ×1) / Velcanto (names8 ×1) |
| メイリィ | Marie (names8, speaker ×4) / Mary (speaker ×2) |
| ロイド | Roméo ×3 / Loid ×1 |
| アスモデウス | Asmodeus (dialog ×26) / Asmodeus??? (names8) |
| ハイランダー | Montagnard (label) / combattants des montagnes, montagnards (dialog) |
| フェザーフォルク | Peuple Ailé (label) / pluméen (dialog ×9) |
| ほうじゅつし, もんしょうつかい | Magic User, Heraldry Wizard (English) |
| 七星 | Grande Ourse (moves) / Sept Étoiles ×3 + Sept Etoiles ×1 (遺跡 sign) |
| 奥義 vs ひっさつわざ | both rendered "arcane" (奥義 = ohgi in descriptions) |
| 12 of 42 spells | menu16 desc name ≠ 8x8/16x16 (see Spells) |
| アシッドレイン | Smog (8x8) / PluieAcide (16x16) / Pluie acide (desc) |
| プロテクション | Garde+ / Protection / Bouclier |
| レイズデッド | Lazzarus (8x8, 16x16) / Lazarus (desc) |
| 22 special moves | desc name ≠ 16x16 (see Special moves) |
| 朱雀翔撃破 | Victoire (sword) / Triomphe (fist) de l'oiseau vermillon; desc: Souffle du moineau ×2 |
| 空破斬 | C.Aérien (8x8) / Air Slash (16x16, label) / Rafale (desc) |
| ダンシングソード | É.Dansant / Dancing Sword / Lame dansante |
| names8 `$0C38–$0C3B` | 8x8 shifted: 気功掌 → Pd.Qigong, 流星掌 → Tonnerre, 練気拳 → Emprise, 気功蹴 → Blâmes (labels8: PaumeQig., PaumeMété, P.Psych, Pd.Qigong) |
| 鑑定 | Expert (label) / Savant (menu16); めきき also Expert |
| 修行 | Bosseur (label) / Entraînement (menu16) |
| ピエティ | Piété (label) / Théologie (desc) |
| レジスト / 作戦 | Régler / Config.; Stratégie / Tactique |
| しょうひMP | Coût PM (names8) / PM Requis (labels8) |
| NEXT, STR… | Suivant/Suiv, Force/Forc (long vs 8x8, intended) |
| 道具屋 (sign) | Quincaillerie ×6 / Magasin d'équipement ×1 / Maison du bricolage ×1 / Brico-malin ×1 |
| 食料品店 | Épicerie ×6 / Epicerie ×1 |
| アストラル城下町 | ville fortifiée d'Astral ×2 / Ville du château d'Astral ×1 / Château d'Astral ×1 |
| アストラル洞窟 | grottes ×2 / grotte ×1 |
| ヴァン・イ・イル城門 | Château de Van I Il ×1 (should be Portes) |
| 廊下 / 書斎 | Couloir ×1 / Corridor ×1 ; Étude ×1 / Salle d'étude ×1 |
| ギルドマスター | Maître de la guilde ×27 / Maitre ×7 / Maître de la Guilde ×3 |
| アドバイザー | Conseiller ×9 / Entraîneur ×4 / Entraineur ×1 |
| 母親 | Mère ×16 (as written: [nick:ラティ]の母親 = Mère de Ratix, レミアの母親 = Mère de Lemia; お母さん = Maman) |
| 主人 | Vieil homme ×8 / Tenancier ×5 / Badam ×2 / Commerçant ×1 |
| 剣士 | Chevalier ×7 / Combattant ×6 |
| フレアバゼラード, アサシンダガー | both "Poignard" |
| スターリング, アストラルリング | both "BagueAstro" |
| クレリック, ラルヴァ | both "Larve" |
| よりょくはのこすな, ちからをつかいきれ | both "Sans retenue" |
| ？FOOD | ?Vivres / ?VBullixir (typo, fixed) |
| Music titles | DANCE DE L'EPEE, PAIX SPACIALE, DEFIT (typos) |

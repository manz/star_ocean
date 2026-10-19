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
- **8x8 names**: items and spells ≤ 10 chars, special moves ≤ 11. To fit:
  - CamelCase compounds, no space: `BagueFée`, `MailForge`, `BicÉtude`, `ChatRubis`;
  - head noun cut to initial + dot: `É.` épée, `B.` bague/bâton, `C.` capel/contre, `Gr.` grève, `O.` orbe, `D.` danse/double,
    `Pg.` poing, `Id.` idole, `Fig.` figurine, `Col.` collier, `Arm.` armure, `Cr.`/`Crist.` cristal;
  - initials as suffix: `GO` Grande Ourse, `DA`/`DN`/`DR` dragon azur/noir/rouge, `OV` oiseau vermillon;
  - `+1`/`+2` kept, `MK2` → `V2`.
- **Item series by suffix**: ポーション/ボトル/ポット → `-ixir` (Bullixir, Fusixir, Fruitixir); ボム → `-otov`
  (Toxotov, Puantotov, Psychotov, Flambotov; stronger = `+`); キュア… → `Médi-`; ミスト → `Nuée-`; シロップ → `Miel-`.
- **Unidentified**: `？WEAPON` → `?Arme`, `？GUARD` → `?Défense`, `？ITEM` → `?Réserve`, `？JEM` → `?Gemme`,
  `？JEWELRY` → `?Bijou`, `？HERB` → `?Herbe`, `？FOOD` → `?Vivres`.
- **Enemies**: French or classic tabletop names (Otyugh, Grell, Aarakocra, Yochlol), with pop-culture nods
  (Shai-Hulud, Sauron, Arsène, Hannibal; item Gloubi-B.). `…シェイプ` series → `-oïde`.

## Characters

### Party

| JP full | JP 8x8 | FR full (names8) | FR 8x8 | Dialog | note |
|---|---|---|---|---|---|
| ラティクス | ラティ | Ratix | Raty | Ratix | |
| ミリー | ミリー | Millie | Milly | Milly | full ≠ short |
| ドーン | ドーン | Dorn | Dorn | Dorn | |
| ロニキス | ロニキス | Ronixis | Ronix | Ronixis | |
| イリア | イリア | Iria | Iria | Iria | |
| シウス | シウス | Cius | Cius | Cius | |
| ヨシュア | ヨシュア | Joshua | Joshua | Joshua | |
| ティニーク | ティニ | Tinek | Tini | Tinek | |
| マーヴェル | マーヴェ | Marvel | Marv | Marvel | |
| アシュレイ | アシュ | Ashlay | Ash | Ashlay | |
| ペリシー | ペリシー | Perisie | Péri | Perisie | |
| フィア | フィア | Fear | Fear | Fear | |
| ルーン | ルーン | Rune | Dorn | - | 8x8 `$000D` = "Dorn" (bug) |

Dialog renders both `[nick:]` and `[name:]` as the full name (`tools/encode_text.py` NAMES).

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
| メトークス山 / 山頂 | Mt Métox / Sommet du Mt Métox | |
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

Head abbreviations: see Conventions. Families: ソード → `Épée…`/`É.…`, リング → `Bague…`/`B.…`, ヘルム → `Capel…`/`C.…`,
グリーブ → `Grève…`/`Gr.…`, シールド → `Écu…`, ガード → `Garde…`, ブーツ → `Botte…`, ボウ → `Arc…`, ローブ → `Robe…`,
スーツ → `Habit…`, アイドル → `Idole…`, チェック → `Torque…`, シンボル → `Signe…`, ぞう → `Fig.…`, しょうぞうがA–L → `PortraitA–L`,
ドワーヴン → `Nain`, エルヴン → `Elfe`, シルヴァン → `Sylve`, ホーリィ → `Bénie/Bénit`, ねこ → `Chat`, ミスリル → `Mithril`,
ごうかな → `…Luxe`, ミラージュ → `…Mirage`. Japanese sake names kept in romaji (Ichinokura, Senchû, YaegakiMu, Tamano, Bijôbu, KokuRyû).

| JP | FR 8x8 |
|---|---|
| バブルポーション | Bullixir |
| メルトポーション | Fusixir |
| スティンクポット | Shlinguixir |
| ビターポーション | Âcrixir |
| フルーツポット | Fruitixir |
| フレッシュボトル | Ravigotant |
| ポイズンボム / キラーポイズン | Toxotov / Toxotov+ |
| スティンクボム / ピコピヨボム | Puantotov / Puantotov+ |
| マインドボム / ギガマインドボム | Psychotov / Psychotov+ |
| フレアボム / メガフレアボム | Flambotov / Flambotov+ |
| スイートシロップ / サワーシロップ / ミックスシロップ | MielDoux / MielAigre / MielMêlé |
| ホーリィミスト | BuéeBénie |
| フェアリィグラス / フェアリィミスト | Féérixir / NuéeFée |
| リザレクトミスト / リザレクトボトル | NuéeLazare / BrocLazare |
| キュアポイズン / キュアパラライズ / キュアストーン | MédiPoison / MédiParal / MediRoche |
| ウィッチパウダー / エルヴンパウダー | Limpinpine / Elfinine |
| シンデレラグラス | Cendrillon |
| ウィルポーション / マイトポーション / スペルポーション | Volontixir / Couragixir / Magixir |
| マジックカード / マジックカラー | Magicarte / Magichrome |
| リサーチペン / クリエイターペン | BicÉtude / BicŒuvre |
| スミスハンマー / ミックスハンマー | MailForge / MailPilon |
| スペクタクルズ | Bésicles |
| けんじゃのいし | Alkahest |
| ムーナイト / ミーティアライト | Sélénite / Météorite |
| オリハルコン / ダマスクス / ルーンメタル | Orichalque / Damas / MétalRune |
| レインボーダイヤ | Iridiamant |
| アルテミスリーフ / シャドゥフラウア / セボリー | Anthémis / Sarracenia / Sauge |
| フェアリィリング / ルナテックリング / スターリング | BagueFée / BagueLune / BagueAstro |
| リフレクトリング / レジストリング | B.Reflet / B.Résist |
| ポイズンチェック / パラライチェック / ストーンチェック | TorquePois / TorquePara / TorqueRoc |
| リバースドール | Retounaît |
| プリティアイドル / ルビーペルシャ | IdoleMimi / ChatRubis |
| フィートシンボル / ミスティシンボル | SigneTotem / SigneBrume |
| ぶさいくなゆびわ / へんなかたまり / わらえるかたまり | BagueTorse / Machin / TrucDrôle |
| せいぶつりろん / やくそうずかん / ぶんぽうろん | Biologie / DePlantis / Bled |
| よげんしょ / どーじん | Prophéties / FanArt |
| せんそうゼリー / まずいデザート | Jell-O / Gloubi-B. |
| やすいさしみ / まずいシチュー / かたいステーキ | Poiscaille / Tambouille / Semelle |
| VICTORY / CRITICAL / PHOENIX / TREASURE / UPSTART | Victoire / Critique / Phénix / Trésor / Avide |
| はやぶさのぞう / どくろのぞう | Fig.Faucon / Fig.Crâne |
| らくがき | Croûte |
| ストラングソード / マーヴェルソード | É.Ficelée / ÉpéeInouïe |
| ソウルイーター / スティルソード | BuveuseÂme / Empêtreuse |
| グローサルソード / ガンブレイド | Crescendo / Pistolame |
| スレイヤーソード / ドゥームブレイド | Dévoreuse / Jugeresse |
| バハムートティア / ムラサマブレード | LarmeBaham / Muramasa |
| なまくらソード / ガラクタ | É.Émoussée / Déchets |
| ロングソード / ロングソード＋1 | É.Longue / É.Longue+1 |
| トゥハンドソード / ツヴァイハンダー | Montante / Espadon |
| ハグナク / さんせつこん | BaghNakha / Nunchaku |
| セントハルバード / スピニングスピア | Hallebénie / Rotolance |
| アルヴァレスト | Cranequin |
| バンデッドメイル / リングメイル / プレートメイル | A.Laminée / Jaseran / Lamellaire |
| ホーリィクローク / ぶどうぎ | Scapulaire / Keikogi |
| プリティビキニ / マジカルビキニ | Bikimimi / Magikini |
| プレートヘルム / デュエルヘルム | Armet / SaladeDuel |
| ラウンドシールド / ナイツシールド | Rondache / ÉcuCroisé |
| ぶどうシューズ | Tsuranuki |
| ミスリルメッシュ | Mithriline |
| バニーホイッスル / ハトのえさ | AppelLapin / Graines |
| おムスビ / はっけおうぎしょ | BouleRiz / Parchemin |

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
| 母親 | Mère de Dorn ×7 / Mère de Ratix ×4 / Maman de Marie ×2 / other ×3 |
| 主人 | Vieil homme ×8 / Tenancier ×5 / Badam ×2 / Commerçant ×1 |
| 剣士 | Chevalier ×7 / Combattant ×6 |
| フレアバゼラード, アサシンダガー | both "Poignard" |
| スターリング, アストラルリング | both "BagueAstro" |
| クレリック, ラルヴァ | both "Larve" |
| よりょくはのこすな, ちからをつかいきれ | both "Sans retenue" |
| ？FOOD | ?Vivres / ?VBullixir (typo) |
| Music titles | DANCE DE L'EPEE, PAIX SPACIALE, DEFIT (typos) |

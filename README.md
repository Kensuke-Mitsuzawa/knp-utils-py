# What's this ?

- Wrapper functions for Japanese parser [KNP](http://nlp.ist.i.kyoto-u.ac.jp/?KNP)
- This package run KNP as multi-threading job using sqlite3 as backend DB

Please visit [Github page](https://github.com/Kensuke-Mitsuzawa/knp-utils-py) also.

# Contribution

- Faster processing-time than other ways to call KNP
- Json style I/O, thus you can call it as API like
- Commandline interface

At my environment(MacBook Pro Early2015)
Each way takes following time for processing 24 input-documents.

```
[knp-utils] elapsed_time:14.52339506149292 [Sec]
[Native KNP subprocess] elapsed_time:23.880084991455078 [Sec]
[Native KNP server] elapsed_time:22.08908200263977 [Sec]
[Pyknp] elapsed_time:36.08908200263977 [Sec]
```

# Requirement

- Juman
- KNP
- Sqlite3
- Python
    - 2.x (checked under 2.7)
    - 3.x (checked under 3.5)

# Setup

## Juman

```
% wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/juman/juman-7.01.tar.bz2&name=juman-7.01.tar.bz2" -O juman-7.01.tar.bz2
% tar jxf juman-7.01.tar.bz2
% cd juman-7.01
% ./configure && make  && make install
```

## KNP

```
% wget "http://nlp.ist.i.kyoto-u.ac.jp/DLcounter/lime.cgi?down=http://nlp.ist.i.kyoto-u.ac.jp/nl-resource/knp/knp-4.16.tar.bz2&name=knp-4.16.tar.bz2" -O knp-4.16.tar.bz2
% tar jxf knp-4.16.tar.bz2
% cd /knp-4.16
% ./configure && make  && make install
```

## package

```
python setup.py install
```

# Sample

## From python code

See `example.py`

## From CL

### Input json file

```
% cat tests/resources/input_sample.json 
[
  {"text-id": "sample-1", "text": "これはテスト文です。"},
  {"text-id": "sample-2", "text": "陪審員の人数は6～12名である場合が多く、その合議体を「陪審」という。陪審は、刑事事件では原則として被告人の有罪・無罪について、民事事件では被告の責任の有無や損害賠償額等について判断する。"},
  {"text-id": "sample-3", "text": "『大脱走』（だいだっそう、原題: The Great Escape）は、1963年公開のアメリカ映画。戦闘シーンのない集団脱走を描いた異色の戦争映画。監督はジョン・スタージェス。出演はスティーブ・マックイーン 、ジェームズ・ガーナー、チャールズ・ブロンソン 、ジェームズ・コバーン 、リチャード・アッテンボロー 、デヴィッド・マッカラム など。"},
  {"text-id": "sample-4", "text": "『ローマの休日』（ローマのきゅうじつ、原題：Roman Holiday）は、1953年製作のアメリカ映画。"},
  {"text-id": "sample-5", "text": "Netscapeシリーズ（ネットスケープ シリーズ）とは、ジム・クラークと NCSA Mosaic（NCSA モザイク）の開発を抜けたマーク・アンドリーセン、ジェイミー・ザヴィンスキーらによって開発されたネットスケープコミュニケーションズのウェブブラウザである Netscape Navigator（ネットスケープ・ナビゲーター）を起源とするウェブブラウザシリーズ。日本では「ネスケ」や「NN」といった略称でも呼ばれた。2008年2月をもってサポートを終了した。"}
]%   
```

### Command to run

```
python knp_utils.py -i ./tests/resources/input_sample.json
```

### Output

```
[{"timestamp": "2017-02-04 00:56:19.922934", "status": 1, "sub_id": "sample-1", "update_at": "2017-02-04 00:56:19.922941", "parsed_result": "# S-ID:1 KNP:4.16-CF1.1 DATE:2017/02/04 SCORE:-18.60959\n* 1D <文頭><ハ><助詞><体言><指示詞><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:これ/これ><主辞代表表記:これ/これ>\n+ 2D <文頭><ハ><助詞><体言><指示詞><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><省略解析対象指示詞><正規化代表表記:これ/これ><解析格:ガ>\nこれ これ これ 指示詞 7 名詞形態指示詞 1 * 0 * 0 \"疑似代表表記 代表表記:これ/これ\" <疑似代表表記><代表表記:これ/これ><正規化代表表記:これ/これ><文頭><かな漢字><ひらがな><自立><内容語><タグ単位始><文節始><文節主辞>\nは は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* -1D <文末><サ変><句点><体言><用言:判><レベル:C><区切:5-5><ID:（文末）><裸名詞><係:文末><提題受:30><主節><格要素><連用要素><動態述語><敬語:丁寧表現><正規化代表表記:テスト/てすと+文/ぶん><主辞代表表記:文/ぶん><主辞’代表表記:テスト/てすと+文/ぶん>\n+ 2D <文節内><係:文節内><サ変><体言><名詞項候補><先行詞候補><非用言格解析:動><態:未定><正規化代表表記:テスト/てすと>\nテスト てすと テスト 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:テスト/てすと カテゴリ:抽象物 ドメイン:教育・学習\" <代表表記:テスト/てすと><カテゴリ:抽象物><ドメイン:教育・学習><正規化代表表記:テスト/てすと><記英数カ><カタカナ><名詞相当語><サ変><自立><内容語><タグ単位始><文節始><固有キー>\n+ -1D <文末><句点><体言><用言:判><レベル:C><区切:5-5><ID:（文末）><裸名詞><係:文末><提題受:30><主節><格要素><連用要素><動態述語><敬語:丁寧表現><一文字漢字><状態述語><判定詞><名詞項候補><先行詞候補><正規化代表表記:文/ぶん><用言代表表記:文/ぶん><時制-無時制><格関係0:ガ:これ><格解析結果:文/ぶん:判1:ガ/N/これ/0/0/1;ニ/U/-/-/-/-;デ/U/-/-/-/-;時間/U/-/-/-/-;ノ/U/-/-/-/-;修飾/U/-/-/-/-;ガ２/U/-/-/-/-;外の関係/U/-/-/-/->\n文 ぶん 文 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:文/ぶん 漢字読み:音 カテゴリ:抽象物\" <代表表記:文/ぶん><漢字読み:音><カテゴリ:抽象物><正規化代表表記:文/ぶん><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>\nです です だ 判定詞 4 * 0 判定詞 25 デス列基本形 27 NIL <表現文末><かな漢字><ひらがな><活用語><付属>\n。 。 。 特殊 1 句点 1 * 0 * 0 NIL <文末><英記号><記号><付属>\nEOS\n", "text": "これはテスト文です。", "record_id": 0}, {"timestamp": "2017-02-04 00:56:19.922934", "status": 1, "sub_id": "sample-2", "update_at": "2017-02-04 00:56:19.922941", "parsed_result": "# S-ID:1 KNP:4.16-CF1.1 DATE:2017/02/04 SCORE:-186.52124\n* 1D <文頭><助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><正規化代表表記:陪審/ばいしん+員/いん><主辞代表表記:員/いん><主辞’代表表記:陪審/ばいしん+員/いん>\n+ 1D <文節内><係:文節内><文頭><体言><名詞項候補><先行詞候補><正規化代表表記:陪審/ばいしん>\n陪審 ばいしん 陪審 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:陪審/ばいしん カテゴリ:抽象物 ドメイン:政治\" <代表表記:陪審/ばいしん><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:陪審/ばいしん><文頭><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始>\n+ 2D <助詞><連体修飾><体言><係:ノ格><区切:0-4><準主題表現><SM-主体><SM-人><一文字漢字><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:員/いん><Wikipediaエントリ:陪審員><Wikipediaリダイレクト:陪審制>\n員 いん 員 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:員/いん 漢字読み:音 カテゴリ:人\" <代表表記:員/いん><漢字読み:音><カテゴリ:人><正規化代表表記:員/いん><Wikipediaエントリ:陪審員:0-1><Wikipediaリダイレクト:陪審制:0-1><漢字><かな漢字><名詞相当語><自立><肩書同格><複合←><内容語><タグ単位始><文節主辞>\nの の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 2D <ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:人数/にんずう><主辞代表表記:人数/にんずう>\n+ 6D <ハ><助詞><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:人数/にんずう><解析格:ガ>\n人数 にんずう 人数 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:人数/にんずう カテゴリ:数量\" <代表表記:人数/にんずう><カテゴリ:数量><正規化代表表記:人数/にんずう><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nは は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 3D <連体修飾><体言><用言:判><係:連格><レベル:B-><区切:0-5><ID:（形判連体形副名）><連体節><状態述語><正規化代表表記:6/6+～/～+12/12+名/な?名/めい><主辞代表表記:名/な?名/めい><主辞’代表表記:12/12+名/な?名/めい>\n+ 4D <文節内><係:文節内><体言><名詞項候補><先行詞候補><正規化代表表記:6/6>\n6 6 6 名詞 6 普通名詞 1 * 0 * 0 \"疑似代表表記 代表表記:6/6 品詞変更:6-6-6-15-1-0-0\" <疑似代表表記><代表表記:6/6><正規化代表表記:6/6><品詞変更:6-6-6-15-1-0-0-\"疑似代表表記 代表表記:6/6\"><品曖-その他><未知語><記英数カ><英記号><記号><名詞相当語><自立><内容語><タグ単位始><文節始>\n+ 5D <文節内><係:文節内><体言><名詞項候補><先行詞候補><正規化代表表記:～/～>\n～ ～ ～ 名詞 6 普通名詞 1 * 0 * 0 \"疑似代表表記 代表表記:～/～ 品詞変更:～-～-～-15-1-0-0\" <疑似代表表記><代表表記:～/～><正規化代表表記:～/～><品詞変更:～-～-～-15-1-0-0-\"疑似代表表記 代表表記:～/～\"><品曖-その他><未知語><記英数カ><英記号><記号><名詞相当語><自立><複合←><内容語><タグ単位始>\n+ 6D <文節内><係:文節内><体言><名詞項候補><先行詞候補><正規化代表表記:12/12>\n12 12 12 名詞 6 普通名詞 1 * 0 * 0 \"疑似代表表記 代表表記:12/12 品詞変更:12-12-12-15-1-0-0\" <疑似代表表記><代表表記:12/12><正規化代表表記:12/12><品詞変更:12-12-12-15-1-0-0-\"疑似代表表記 代表表記:12/12\"><品曖-その他><未知語><記英数カ><英記号><記号><名詞相当語><自立><複合←><内容語><タグ単位始>\n+ 7D <連体修飾><体言><用言:判><係:連格><レベル:B-><区切:0-5><ID:（形判連体形副名）><連体節><状態述語><一文字漢字><判定詞><名詞項候補><先行詞候補><正規化代表表記:名/な?名/めい><用言代表表記:名/な?名/めい><時制-無時制><格関係2:ガ:人数><格関係7:外の関係:場合><格解析結果:名/めい:判7:ガ/N/人数/2/0/1;ニ/U/-/-/-/-;デ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/N/場合/7/0/1;修飾/U/-/-/-/-;ガ２/U/-/-/-/-;ニタイスル/U/-/-/-/-;ニオク/U/-/-/-/->\n名 めい 名 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:名/めい 漢字読み:音 カテゴリ:抽象物;数量\" <代表表記:名/めい><正規化代表表記:名/な?名/めい><品曖><品曖-普通名詞><原形曖昧><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞><ALT-名-な-名-6-1-0-0-\"代表表記:名/な 漢字読み:訓 カテゴリ:抽象物\"><漢字読み:音><カテゴリ:抽象物;数量><用言曖昧性解消>\nである である だ 判定詞 4 * 0 判定詞 25 デアル列基本形 15 NIL <かな漢字><ひらがな><活用語><付属>\n* 4D <形副名詞><外の関係><ガ><助詞><体言><係:ガ格><区切:0-0><格要素><連用要素><正規化代表表記:場合/ばあい><主辞代表表記:場合/ばあい>\n+ 8D <形副名詞><外の関係><ガ><助詞><体言><係:ガ格><区切:0-0><格要素><連用要素><名詞項候補><省略解析なし><正規化代表表記:場合/ばあい><解析連格:外の関係><解析格:ガ>\n場合 ばあい 場合 名詞 6 副詞的名詞 9 * 0 * 0 \"代表表記:場合/ばあい\" <代表表記:場合/ばあい><正規化代表表記:場合/ばあい><修飾（ニ格）><修飾（デ格）><漢字><かな漢字><名詞相当語><形副名詞><自立><内容語><タグ単位始><文節始><文節主辞>\nが が が 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 8D <読点><用言:形><係:連用><レベル:B><並キ:述:&D:1&&用言:形||&ST:3.0><区切:3-5><ID:〜く><提題受:10><連用要素><連用節><状態述語><正規化代表表記:多い/おおい><主辞代表表記:多い/おおい><並列類似度:1.617>\n+ 13D <読点><用言:形><係:連用><レベル:B><並キ:述:&D:1&&用言:形||&ST:3.0><区切:3-5><ID:〜く><提題受:10><連用要素><連用節><状態述語><正規化代表表記:多い/おおい><用言代表表記:多い/おおい><時制-無時制><格関係7:ガ:場合><格解析結果:多い/おおい:形5:ガ/C/場合/7/0/1;ニ/U/-/-/-/-;ト/U/-/-/-/-;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;ガ２/U/-/-/-/-;修飾/U/-/-/-/-;トスル/U/-/-/-/-;ニツク/U/-/-/-/-;トイウ/U/-/-/-/-;ニヨル/U/-/-/-/-;ニカンスル/U/-/-/-/-;ニオク/U/-/-/-/-;ニトル/U/-/-/-/->\n多く おおく 多い 形容詞 3 * 0 イ形容詞アウオ段 18 基本連用形 7 \"代表表記:多い/おおい 反義:形容詞:少ない/すくない\" <代表表記:多い/おおい><反義:形容詞:少ない/すくない><正規化代表表記:多い/おおい><かな漢字><活用語><自立><内容語><タグ単位始><文節始><文節主辞>\n、 、 、 特殊 1 読点 2 * 0 * 0 NIL <英記号><記号><述語区切><付属>\n* 6D <連体修飾><連体詞形態指示詞><係:連体><区切:0-4><正規化代表表記:その/その><主辞代表表記:その/その>\n+ 11D <連体修飾><連体詞形態指示詞><係:連体><区切:0-4><正規化代表表記:その/その>\nその その その 指示詞 7 連体詞形態指示詞 2 * 0 * 0 \"疑似代表表記 代表表記:その/その\" <疑似代表表記><代表表記:その/その><正規化代表表記:その/その><かな漢字><ひらがな><自立><内容語><タグ単位始><文節始><文節主辞>\n* 8D <サ変><ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><正規化代表表記:合議/ごうぎ+体/からだ?体/たい><主辞代表表記:体/からだ?体/たい><主辞’代表表記:合議/ごうぎ+体/からだ?体/たい>\n+ 11D <文節内><係:文節内><サ変><体言><名詞項候補><先行詞候補><非用言格解析:動><照応ヒント:係><態:未定><正規化代表表記:合議/ごうぎ>\n合議 ごうぎ 合議 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:合議/ごうぎ カテゴリ:抽象物\" <代表表記:合議/ごうぎ><カテゴリ:抽象物><正規化代表表記:合議/ごうぎ><漢字><かな漢字><名詞相当語><サ変><自立><内容語><タグ単位始><文節始>\n+ 13D <ヲ><助詞><体言><係:ヲ格><区切:0-0><格要素><連用要素><一文字漢字><名詞項候補><先行詞候補><正規化代表表記:体/からだ?体/たい><解析格:ヲ>\n体 たい 体 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:体/たい 漢字読み:音 カテゴリ:組織・団体\" <代表表記:体/たい><正規化代表表記:体/からだ?体/たい><品曖><品曖-普通名詞><原形曖昧><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞><ALT-体-からだ-体-6-1-0-0-\"代表表記:体/からだ 漢字読み:訓 カテゴリ:動物\"><漢字読み:音><カテゴリ:組織・団体><名詞曖昧性解消>\nを を を 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 8D <ト><括弧始><括弧終><助詞><体言><係:ト格><並キ:名:&ST:5.0><区切:1-4><並列タイプ:AND><格要素><連用要素><正規化代表表記:陪審/ばいしん><主辞代表表記:陪審/ばいしん><並列類似度:-100.000>\n+ 13D <ト><括弧始><括弧終><助詞><体言><係:ト格><並キ:名:&ST:5.0><区切:1-4><並列タイプ:AND><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:陪審/ばいしん><解析格:ト>\n「 「 「 特殊 1 括弧始 3 * 0 * 0 NIL <記英数カ><英記号><記号><括弧始><括弧><接頭><非独立接頭辞><タグ単位始><文節始>\n陪審 ばいしん 陪審 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:陪審/ばいしん カテゴリ:抽象物 ドメイン:政治\" <代表表記:陪審/ばいしん><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:陪審/ばいしん><漢字><かな漢字><名詞相当語><自立><内容語><文節主辞>\n」 」 」 特殊 1 括弧終 4 * 0 * 0 NIL <記英数カ><英記号><記号><括弧終><括弧><述語区切><付属>\nと と と 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 21P <補文ト><句点><引用内文末><用言:動><係:文末><レベル:C><区切:5-5><ID:（文末）><提題受:30><格要素><連用要素><動態述語><正規化代表表記:言う/いう><主辞代表表記:言う/いう>\n+ 31P <補文ト><句点><引用内文末><用言:動><係:文末><レベル:C><区切:5-5><ID:（文末）><提題受:30><格要素><連用要素><動態述語><省略解析なし><不特定人:ガ><省略格指定><正規化代表表記:言う/いう><用言代表表記:言う/いう><時制-未来><主題格:一人称優位><格関係11:ヲ:体><格関係12:ト:陪審><格解析結果:言う/いう:動3:ガ/U/-/-/-/-;ヲ/C/体/11/0/1;ニ/U/-/-/-/-;ト/C/陪審/12/0/1;デ/U/-/-/-/-;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;ヘ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;修飾/U/-/-/-/-;ノ/U/-/-/-/-;ガ２/U/-/-/-/-;ニツク/U/-/-/-/-;トスル/U/-/-/-/-;ニタイスル/U/-/-/-/-;ニカンスル/U/-/-/-/-;ニヨル/U/-/-/-/-;トイウ/U/-/-/-/->\nいう いう いう 動詞 2 * 0 子音動詞ワ行 12 基本形 2 \"代表表記:言う/いう 補文ト\" <代表表記:言う/いう><補文ト><正規化代表表記:言う/いう><と基本形複合辞><かな漢字><ひらがな><活用語><自立><内容語><タグ単位始><文節始><文節主辞>\n。 。 。 特殊 1 句点 1 * 0 * 0 NIL <英記号><記号><付属>\n* 21D <ハ><読点><助詞><引用内文頭><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><正規化代表表記:陪審/ばいしん><主辞代表表記:陪審/ばいしん>\n+ 31D <ハ><読点><助詞><引用内文頭><体言><係:未格><提題><区切:3-5><主題表現><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:陪審/ばいしん><解析格:ヲ>\n陪審 ばいしん 陪審 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:陪審/ばいしん カテゴリ:抽象物 ドメイン:政治\" <代表表記:陪審/ばいしん><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:陪審/ばいしん><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nは は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n、 、 、 特殊 1 読点 2 * 0 * 0 NIL <英記号><記号><述語区切><付属>\n* 21D <SM-主体><SM-人><デ><ハ><デハ><助詞><体言><係:デ格><区切:3-5><格要素><連用要素><正規化代表表記:刑事/けいじ+事件/じけん><主辞代表表記:事件/じけん>\n+ 16D <文節内><係:文節内><SM-主体><SM-人><体言><名詞項候補><先行詞候補><正規化代表表記:刑事/けいじ>\n刑事 けいじ 刑事 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:刑事/けいじ 人名末尾 カテゴリ:人 ドメイン:政治\" <代表表記:刑事/けいじ><人名末尾><カテゴリ:人><ドメイン:政治><正規化代表表記:刑事/けいじ><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始>\n+ 31D <SM-主体><SM-人><デ><ハ><デハ><助詞><体言><係:デ格><区切:3-5><格要素><連用要素><ルール外の関係><名詞項候補><先行詞候補><正規化代表表記:事件/じけん><Wikipediaエントリ:刑事事件><Wikipediaリダイレクト:刑事手続><解析格:ガ>\n事件 じけん 事件 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:事件/じけん カテゴリ:抽象物 ドメイン:政治\" <代表表記:事件/じけん><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:事件/じけん><Wikipediaエントリ:刑事事件:27-28><Wikipediaリダイレクト:刑事手続:27-28><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>\nで で で 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\nは は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 21D <副詞><修飾><係:連用><区切:0-4><連用要素><連用節><正規化代表表記:原則として/げんそくとして><主辞代表表記:原則として/げんそくとして>\n+ 31D <副詞><修飾><係:連用><区切:0-4><連用要素><連用節><正規化代表表記:原則として/げんそくとして><解析格:修飾>\n原則として げんそくとして 原則として 副詞 8 * 0 * 0 * 0 \"代表表記:原則として/げんそくとして\" <代表表記:原則として/げんそくとして><正規化代表表記:原則として/げんそくとして><かな漢字><自立><内容語><タグ単位始><文節始><文節主辞>\n* 13D <SM-主体><SM-人><助詞><連体修飾><体言><係:ノ格><区切:0-4><正規化代表表記:被告人/ひこくにん><主辞代表表記:被告人/ひこくにん>\n+ 20D <SM-主体><SM-人><助詞><連体修飾><体言><係:ノ格><区切:0-4><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:被告人/ひこくにん>\n被告人 ひこくにん 被告人 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:被告人/ひこくにん カテゴリ:人 ドメイン:政治\" <代表表記:被告人/ひこくにん><カテゴリ:人><ドメイン:政治><正規化代表表記:被告人/ひこくにん><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nの の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 14D <ニ><助詞><体言><係:ニ格><区切:0-0><隣係絶対><格要素><連用要素><正規化代表表記:有罪/ゆうざい+無罪/むざい><主辞代表表記:無罪/むざい>\n+ 20D <文節内><係:文節内><体言><名詞項候補><先行詞候補><正規化代表表記:有罪/ゆうざい>\n有罪 ゆうざい 有罪 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:有罪/ゆうざい カテゴリ:抽象物 ドメイン:政治\" <代表表記:有罪/ゆうざい><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:有罪/ゆうざい><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始>\n・ ・ ・ 特殊 1 記号 5 * 0 * 0 NIL <記英数カ><英記号><記号><付属><複合←>\n+ 21D <ニ><助詞><体言><係:ニ格><区切:0-0><隣係絶対><格要素><連用要素><名詞項候補><先行詞候補><正規化代表表記:無罪/むざい><解析格:ニツク>\n無罪 むざい 無罪 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:無罪/むざい カテゴリ:抽象物 ドメイン:政治\" <代表表記:無罪/むざい><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:無罪/むざい><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>\nに に に 助詞 9 格助詞 1 * 0 * 0 \"連語\" <連語><かな漢字><ひらがな><付属>\n* 21D <読点><用言:動><受:隣のみ><隣受絶対><複合辞><係:複合辞連用><レベル:A-><並キ:？:&ST:3.0&&&自立語一致><区切:0-3><ID:〜について><動態述語><正規化代表表記:つく/つく><主辞代表表記:つく/つく><並列類似度:-100.000><並結句数:2><並結文節数:6>\n+ 31D <読点><用言:動><受:隣のみ><隣受絶対><複合辞><係:複合辞連用><レベル:A-><並キ:？:&ST:3.0&&&自立語一致><区切:0-3><ID:〜について><動態述語><格解析なし><省略解析なし><格要素表記直前参照><正規化代表表記:つく/つく>\nついて ついて つく 動詞 2 * 0 子音動詞カ行 2 タ系連用テ形 14 \"連語 疑似代表表記 代表表記:つく/つく\" <連語><疑似代表表記><代表表記:つく/つく><正規化代表表記:つく/つく><に基本連用形複合辞><にタ系連用テ形複合辞><かな漢字><ひらがな><活用語><自立><内容語><タグ単位始><文節始><文節主辞>\n、 、 、 特殊 1 読点 2 * 0 * 0 NIL <英記号><記号><述語区切><付属>\n* 21D <デ><ハ><デハ><助詞><体言><係:デ格><区切:3-5><格要素><連用要素><正規化代表表記:民事/みんじ+事件/じけん><主辞代表表記:事件/じけん>\n+ 23D <文節内><係:文節内><体言><名詞項候補><先行詞候補><正規化代表表記:民事/みんじ>\n民事 みんじ 民事 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:民事/みんじ カテゴリ:抽象物 ドメイン:政治\" <代表表記:民事/みんじ><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:民事/みんじ><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始>\n+ 31D <デ><ハ><デハ><助詞><体言><係:デ格><区切:3-5><格要素><連用要素><ルール外の関係><名詞項候補><先行詞候補><正規化代表表記:事件/じけん><Wikipediaエントリ:民事事件><Wikipediaリダイレクト:民事><解析格:デ>\n事件 じけん 事件 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:事件/じけん カテゴリ:抽象物 ドメイン:政治\" <代表表記:事件/じけん><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:事件/じけん><Wikipediaエントリ:民事事件:40-41><Wikipediaリダイレクト:民事:40-41><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>\nで で で 助詞 9 格助詞 1 * 0 * 0 NIL <かな漢字><ひらがな><付属>\nは は は 助詞 9 副助詞 2 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 17D <SM-主体><SM-人><助詞><連体修飾><体言><係:ノ格><区切:0-4><正規化代表表記:被告/ひこく><主辞代表表記:被告/ひこく>\n+ 25D <SM-主体><SM-人><助詞><連体修飾><体言><係:ノ格><区切:0-4><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:被告/ひこく>\n被告 ひこく 被告 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:被告/ひこく 人名末尾 カテゴリ:人 ドメイン:政治\" <代表表記:被告/ひこく><人名末尾><カテゴリ:人><ドメイン:政治><正規化代表表記:被告/ひこく><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nの の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 19D <助詞><連体修飾><体言><係:ノ格><区切:0-4><正規化代表表記:責任/せきにん><主辞代表表記:責任/せきにん>\n+ 29D <助詞><連体修飾><体言><係:ノ格><区切:0-4><名詞項候補><先行詞候補><係チ:非用言格解析||用言&&文節内:Ｔ解析格-ヲ><正規化代表表記:責任/せきにん>\n責任 せきにん 責任 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:責任/せきにん カテゴリ:抽象物\" <代表表記:責任/せきにん><カテゴリ:抽象物><正規化代表表記:責任/せきにん><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nの の の 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 19P <助詞><体言><係:連体:ヤ><並キ:名><区切:1-2><並列タイプ:AND><正規化代表表記:有無/うむ><主辞代表表記:有無/うむ><並列類似度:4.516><並結句数:2><並結文節数:1>\n+ 29P <助詞><体言><係:連体:ヤ><並キ:名><区切:1-2><並列タイプ:AND><名詞項候補><先行詞候補><正規化代表表記:有無/うむ>\n有無 うむ 有無 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:有無/うむ カテゴリ:抽象物\" <代表表記:有無/うむ><カテゴリ:抽象物><正規化代表表記:有無/うむ><漢字><かな漢字><名詞相当語><自立><内容語><タグ単位始><文節始><文節主辞>\nや や や 助詞 9 接続助詞 3 * 0 * 0 NIL <かな漢字><ひらがな><付属>\n* 20D <サ変><ニ><助詞><体言><係:ニ格><区切:0-0><隣係絶対><格要素><連用要素><正規化代表表記:損害/そんがい+賠償/ばいしょう+額/がく><主辞代表表記:額/がく><主辞’代表表記:賠償/ばいしょう+額/がく>\n+ 28D <文節内><係:文節内><サ変><体言><名詞項候補><先行詞候補><非用言格解析:動><照応ヒント:係><態:未定><正規化代表表記:損害/そんがい>\n損害 そんがい 損害 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:損害/そんがい カテゴリ:抽象物\" <代表表記:損害/そんがい><カテゴリ:抽象物><正規化代表表記:損害/そんがい><漢字><かな漢字><名詞相当語><サ変><自立><内容語><タグ単位始><文節始>\n+ 29D <文節内><係:文節内><サ変><体言><名詞項候補><先行詞候補><非用言格解析:動><照応ヒント:係><態:未定><正規化代表表記:賠償/ばいしょう><Wikipedia上位語:法律用語><Wikipediaエントリ:損害賠償>\n賠償 ばいしょう 賠償 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:賠償/ばいしょう カテゴリ:抽象物 ドメイン:政治\" <代表表記:賠償/ばいしょう><カテゴリ:抽象物><ドメイン:政治><正規化代表表記:賠償/ばいしょう><Wikipedia上位語:法律用語:50-51><Wikipediaエントリ:損害賠償:50-51><漢字><かな漢字><名詞相当語><サ変><自立><複合←><内容語><タグ単位始>\n+ 30D <ニ><助詞><体言><係:ニ格><区切:0-0><隣係絶対><格要素><連用要素><一文字漢字><名詞項候補><先行詞候補><正規化代表表記:額/がく><解析格:ニ>\n額 がく 額 名詞 6 普通名詞 1 * 0 * 0 \"代表表記:額/がく 漢字読み:音 カテゴリ:人工物-金銭;人工物-その他\" <代表表記:額/がく><漢字読み:音><カテゴリ:人工物-金銭;人工物-その他><正規化代表表記:額/がく><漢字><かな漢字><名詞相当語><自立><複合←><内容語><タグ単位始><文節主辞>\n等 とう 等 接尾辞 14 名詞性名詞接尾辞 2 * 0 * 0 \"代表表記:等/とう\" <代表表記:等/とう><正規化代表表記:等/とう><漢字><かな漢字><名詞相当語><付属>\nに に に 助詞 9 格助詞 1 * 0 * 0 \"連語\" <連語><かな漢字><ひらがな><付属>\n* 21D <用言:動><受:隣のみ><隣受絶対><複合辞><係:複合辞連用><レベル:A-><並キ:？:&ST:3.0&&&自立語一致><区切:0-3><ID:〜について><動態述語><正規化代表表記:つく/つく><主辞代表表記:つく/つく><並列類似度:-100.000>\n+ 31D <用言:動><受:隣のみ><隣受絶対><複合辞><係:複合辞連用><レベル:A-><並キ:？:&ST:3.0&&&自立語一致><区切:0-3><ID:〜について><動態述語><格解析なし><省略解析なし><格要素表記直前参照><正規化代表表記:つく/つく>\nついて ついて つく 動詞 2 * 0 子音動詞カ行 2 タ系連用テ形 14 \"連語 疑似代表表記 代表表記:つく/つく\" <連語><疑似代表表記><代表表記:つく/つく><正規化代表表記:つく/つく><に基本連用形複合辞><にタ系連用テ形複合辞><かな漢字><ひらがな><活用語><自立><内容語><タグ単位始><文節始><文節主辞>\n* -1D <文末><補文ト><サ変><サ変動詞><句点><用言:動><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><動態述語><正規化代表表記:判断/はんだん><主辞代表表記:判断/はんだん>\n+ -1D <文末><補文ト><サ変動詞><句点><用言:動><レベル:C><区切:5-5><ID:（文末）><係:文末><提題受:30><主節><格要素><連用要素><動態述語><サ変><正規化代表表記:判断/はんだん><用言代表表記:判断/はんだん><時制-未来><主題格:一人称優位><格関係14:ヲ:陪審><格関係16:ガ:事件><格関係17:修飾:原則として><格関係20:ニツク:無罪><格関係23:デ:事件><格関係29:ニ:額><格解析結果:判断/はんだん:動4:ガ/C/事件/16/0/1;ヲ/N/陪審/14/0/1;ニ/C/有無/26/0/1;ニ/C/額/29/0/1;デ/C/事件/23/0/1;カラ/U/-/-/-/-;ヨリ/U/-/-/-/-;マデ/U/-/-/-/-;時間/U/-/-/-/-;外の関係/U/-/-/-/-;ノ/U/-/-/-/-;修飾/C/原則として/17/0/1;ニヨル/U/-/-/-/-;ニモトヅク/U/-/-/-/-;ニツク/C/無罪/20/0/1;トスル/U/-/-/-/-;ニオク/U/-/-/-/-;ニソウ/U/-/-/-/-;ニタイスル/U/-/-/-/-;ヲツウジル/U/-/-/-/-;ヲフクメル/U/-/-/-/->\n判断 はんだん 判断 名詞 6 サ変名詞 2 * 0 * 0 \"代表表記:判断/はんだん 補文ト カテゴリ:抽象物\" <代表表記:判断/はんだん><補文ト><カテゴリ:抽象物><正規化代表表記:判断/はんだん><漢字><かな漢字><名詞相当語><サ変><サ変動詞><自立><内容語><タグ単位始><文節始><文節主辞>\nする する する 動詞 2 * 0 サ変動詞 16 基本形 2 \"代表表記:する/する 付属動詞候補（基本） 自他動詞:自:成る/なる\" <代表表記:する/する><付属動詞候補（基本）><自他動詞:自:成る/なる><正規化代表表記:する/する><表現文末><とタ系連用テ形複合辞><かな漢字><ひらがな><活用語><付属>\n。 。 。 特殊 1 句点 1 * 0 * 0 NIL <文末><英記号><記号><付属>\nEOS\n", "text": "陪審員の人数は6～12名である場合が多く、その合議体を「陪審」という。陪審は、刑事事件では原則として被告人の有罪・無罪について、民事事件では被告の責任の有無や損害賠償額等について判断する。", "record_id": 1}, {"timestamp": "2017-02-04 00:56:19.922934", "status": 1, "sub_id": "sample-3", "update_at": "2017-02-04 00:56:19.922941", "parsed_result": "# S-ID:1 KNP:4.16-CF1.1 DATE:2017/02/04 SCORE:0.00000 ERROR:Cannot make mrph\nEOS\n", "text": "『大脱走』（だいだっそう、原題: The Great Escape）は、1963年公開のアメリカ映画。戦闘シーンのない集団脱走を描いた異色の戦争映画。監督はジョン・スタージェス。出演はスティーブ・マックイーン 、ジェームズ・ガーナー、チャールズ・ブロンソン 、ジェームズ・コバーン 、リチャード・アッテンボロー 、デヴィッド・マッカラム など。", "record_id": 2}, {"timestamp": "2017-02-04 00:56:19.922934", "status": 1, "sub_id": "sample-4", "update_at": "2017-02-04 00:56:19.922941", "parsed_result": "# S-ID:1 KNP:4.16-CF1.1 DATE:2017/02/04 SCORE:0.00000 ERROR:Cannot make mrph\nEOS\n", "text": "『ローマの休日』（ローマのきゅうじつ、原題：Roman Holiday）は、1953年製作のアメリカ映画。", "record_id": 3}, {"timestamp": "2017-02-04 00:56:19.922934", "status": 1, "sub_id": "sample-5", "update_at": "2017-02-04 00:56:19.922941", "parsed_result": "# S-ID:1 KNP:4.16-CF1.1 DATE:2017/02/04 SCORE:0.00000 ERROR:Cannot make mrph\nEOS\n", "text": "Netscapeシリーズ（ネットスケープ シリーズ）とは、ジム・クラークと NCSA Mosaic（NCSA モザイク）の開発を抜けたマーク・アンドリーセン、ジェイミー・ザヴィンスキーらによって開発されたネットスケープコミュニケーションズのウェブブラウザである Netscape Navigator（ネットスケープ・ナビゲーター）を起源とするウェブブラウザシリーズ。日本では「ネスケ」や「NN」といった略称でも呼ばれた。2008年2月をもってサポートを終了した。", "record_id": 4}]
```
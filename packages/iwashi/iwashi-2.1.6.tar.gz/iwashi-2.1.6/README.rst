Profile Link Tree Generator
===========================

.. image:: https://img.shields.io/github/license/mashape/apistatus.svg
    :target: http://opensource.org/licenses/MIT
.. image:: https://badge.fury.io/py/iwashi.svg
    :target: https://badge.fury.io/py/iwashi

Installation
------------

.. code:: bash

    pip install iwashi

Usage
-----

in command line

.. code:: bash

    python -m iwashi <url>

in code

.. code:: python

    import iwashi

    result = iwashi.visit('https://www.youtube.com/@HikakinTV')

    iwashi.helper.print_result(result)

    """
    Youtube
    │url  : https://www.youtube.com/channel/UCZf__ehlCEBPop-_sldpBUQ    
    │name : HikakinTV
    │score: 1.0
    │links : []
    │description: いつも見てくれてありがとう。\n◆プロフィール◆\nYouTube にてHIKAKIN、HikakinTV、HikakinGames、HikakinBlogと\n４つのチャンネ ルを運営し、動画の総アクセス数は150億回を突破、\nチャンネル登録者数 は計1800万人以上、YouTubeタレント事務所uuum株式会社ファウンダー兼最 高顧問。
        Twitter
        │url  : https://twitter.com/hikakin
        │name : HIKAKIN😎ヒカキン 【YouTuber】
        │score: 1.0
        │links : ['https://www.youtube.com/channel/UCZf__ehlCEBPop-_sldpBUQ']
        │description: ユーチューバー。2006年からYouTubeやってます。YouTube&SNSフォロワー計2900万人突破。再生回数計180億回。UUUM株式会社最高 顧問&ファウンダー。インスタTikTokもフォロー是非 ！コラボ依頼やお仕事依頼などのDMは一切返信出来ませんので全て事務所までお願いします！    
        Youtube
        │url  : https://www.youtube.com/channel/UClLV6D8S4CrVJL64-aQvwTw
        │name : HIKAKIN
        │score: 1.0
        │links : ['https://twitter.com/hikakin']
        │description: I'm a Japanese Beatboxer.\n\n◆プロフィール◆\nYouTubeにてHIKAKIN、HikakinTV、HikakinGames、HikakinBlogと\n４つのチャン ネルを運営し、動画の総アクセス数は100億回を突破、\nチャンネル登録者 数は計1800万人以上、月間アクセス2億回達成。\nYouTubeタレント事務所uuum株式会社ファウンダー兼最高顧問。\nビートボックスにおいては、ポップからゲームミュージックに至るまで\n様々なジャンルを口だけで再現するそのスキルは世界中から絶賛され、\n数多くの人を魅了している。2013年にはエアロスミスのツアーに参加。\nシンガポール、大阪で共演し世界中にその名を轟かせた。\nビートボックス以外にもHikakinTVチャンネルでは登録者500万人を超え、\n顔出しブロガーとしては日本で最も視聴されており、新たに開設した\nゲーム実況のHikakinGamesチャンネルにおいても登録者300万 人を超え、\nゲーム実況ジャンルにおいて日本最大級のチャンネルになっている。
            Bitly
            │url  : https://bit.ly/HIKAKIN
            │name : None
            │score: 1.0
            │links : ['https://www.youtube.com/channel/UClLV6D8S4CrVJL64-aQvwTw']
            facebook.com
            │url  : http://www.facebook.com/HIKAKIN
            │name : None
            │score: 1.0
            │links : []
            plus.google.com
            │url  : https://plus.google.com/108607724554070105904/posts 
            │name : None
            │score: 1.0
            │links : []
            Soundcloud
            │url  : https://soundcloud.com/hikakin
            │name : HIKAKIN
            │score: 1.0
            │links : []
            Bitly
            │url  : https://bit.ly/HikakinBlog
            │name : None
            │score: 1.0
            │links : ['https://www.youtube.com/channel/UCQMoeRP9SDaFipXDBIp3pFA']
            Twitter
            │url  : https://twitter.com/HikakinBeatbox
            │name : hikakinbeatbox
            │score: 1.0
            │links : ['https://twitter.com/hikakin']
            │description: 以前Hikakinが使っていたアカウントです。現在は@hikakinでやっています。青い公式マークのついたアカウントが本物のHikak\n現在のアカウントはこちら↓
            facebook.com
            │url  : http://www.facebook.com/HIKAKIN
            │name : None
            │score: 1.0
            │links : []
    """
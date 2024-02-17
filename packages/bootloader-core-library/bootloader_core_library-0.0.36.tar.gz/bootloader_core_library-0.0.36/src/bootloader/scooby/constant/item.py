# Copyright (C) 2023 Bootloader.  All rights reserved.
#
# This software is the confidential and proprietary information of
# Bootloader or one of its subsidiaries.  You shall not disclose this
# confidential information and shall use it only in accordance with the
# terms of the license agreement or other applicable agreement you
# entered into with Bootloader.
#
# BOOTLOADER MAKES NO REPRESENTATIONS OR WARRANTIES ABOUT THE
# SUITABILITY OF THE SOFTWARE, EITHER EXPRESS OR IMPLIED, INCLUDING BUT
# NOT LIMITED TO THE IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR
# A PARTICULAR PURPOSE, OR NON-INFRINGEMENT.  BOOTLOADER SHALL NOT BE
# LIABLE FOR ANY LOSSES OR DAMAGES SUFFERED BY LICENSEE AS A RESULT OF
# USING, MODIFYING OR DISTRIBUTING THIS SOFTWARE OR ITS DERIVATIVES.

from majormode.perseus.model import enum


# The various types, also known as *categories*, of items.
ItemType = enum.Enum(
    # Articles carried (purses and handbags, hand fans, parasols and
    # umbrellas, wallets, canes, and ceremonial swords) rather than worn
    # normally, items worn on a single part of the body and easily removed
    # (jackets, boots and shoes, cravats, ties, hats, bonnets, belts and
    # suspenders, gloves, muffs, necklaces, bracelets, watches, eyewear,
    # sashes, shawls, scarves, lanyards, socks, pins, piercings, rings,
    # and stockings), worn purely for adornment (jewelry), or items that
    # do not serve a protective function.  An accessory is an item used
    # to contribute, in a secondary manner, to an individual's outfit.
    #
    # Common examples of accessories include:
    #
    # - Jewelry: Necklaces, earrings, bracelets, rings, and watches.
    # - Bags: Handbags, clutches, backpacks, and tote bags.
    # - Belts: Worn around the waist to cinch or accessorize clothing.
    # - Scarves: Worn around the neck or as a headpiece to add color and texture.
    # - Hats: Various types of hats like fedoras, beanies, sunhats, etc.
    # - Sunglasses: Both for functional purposes and as a fashion statement.
    # - Gloves: Worn on the hands, typically during colder weather.
    # - Ties and bowties: Mostly worn with formal attire.
    # - Socks and stockings: To add style and comfort to footwear.
    #
    # Accessories are chosen deliberately to complement the outfit and
    # reflect the wearer's personal style.  They can significantly impact
    # the overall appearance of an outfit, taking it from simple to stylish
    # or from formal to casual. individuality in fashion.
    #
    #
    # @note: accessories belong to an outfit. Accessories are items that are
    #     worn or used to complement and enhance an outfit, adding style,
    #     detail, and personality to the overall look.  They are meant to
    #     accessorize or complete the clothing ensemble.
    'Accessory',

    # Any item worn on the body, like shirts, pants, skirts.  Garments
    # cover the body, while hats and headgear cover the head.
    #
    #
    # @note: In the context of Bootloader, shoes, gloves, and hats are
    # intended for the virtual pets, but in real life pets generally don't
    # wear shoes, gloves, and hats.  Therefore, shoes, gloves, and hats are
    # considered as accessories, even if they are also a type of clothing
    # since they are worn on the body and serve a functional purpose of
    # protecting respectively the feet, the hands, and the head.
    #
    #     However, in the context of Bootloader, shoes, gloves, and hats
    #     complement and enhance an outfit, rather than being the primary
    #     clothing piece. They add style, color, and personality to an
    #     outfit.  They can be chosen to match or contrast with the clothing,
    #     creating a specific look or making a fashion statement.
    #
    #     In practical terms, shoes, gloves, and hats are essential clothing
    #     items, especially when it comes to everyday wear and fulfilling
    #     specific functional needs like protection, support, and comfort.
    'Cloth',

    # A combination of clothing items.
    'Outfit',

    # A virtual pet.
    'Pet',

    # Props, formally known as (theatrical) property, are objects that
    # support the scene but are not part of the level layout or character
    # set.
    #
    # Large movable equipment, such as sleeping basket, mirror, lamp, boxes
    # with things to loot, used to make the space suitable for living.
    'PropFurniture',

    # An object for the pet to play with.
    'PropToy',
)

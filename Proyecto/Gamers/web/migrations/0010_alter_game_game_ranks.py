# Generated by Django 4.0.6 on 2022-07-18 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0009_game_game_ranks_alter_gameship_rank'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='game_ranks',
            field=models.CharField(choices=[('un', [('Unranked', 'Unranked')]), ('CSG', [('Silver I', 'Silver I'), ('Silver II', 'Silver II'), ('Silver III', 'Silver III'), ('Silver IV', 'Silver IV'), ('Silver Elite', 'Silver Elite'), ('Silver Elite Master', 'Silver Elite Master'), ('Gold Nova I', 'Gold Nova I'), ('Gold Nova II', 'Gold Nova II'), ('Gold Nova III', 'Gold Nova III'), ('Gold Nova Master', 'Gold Nova Master'), ('Master Guardian I', 'Master Guardian I'), ('Master Guardian II', 'Master Guardian II'), ('Master Guardian Elite', 'Master Guardian Elite'), ('Distinguished Master Guardian', 'Distinguished Master Guardian'), ('Legendary Eagle', 'Legendary Eagle'), ('Legendary Eagle Master', 'Legendary Eagle Master'), ('Supreme Master First Class', 'Supreme Master First Class'), ('The Global Elite', 'The Global Elite')]), ('LOL', [('Iron', 'Iron'), ('Bronze', 'Bronze'), ('Silver', 'Silver'), ('Gold', 'Gold'), ('Platinum', 'Platinum'), ('Diamond', 'Diamond'), ('Master', 'Master'), ('Grand Master', 'Grand Master'), ('Challenger', 'Challenger')]), ('RLE', [('Bronze I', 'Bronze I'), ('Bronze II', 'Bronze II'), ('Bronze III', 'Bronze III'), ('Silver I', 'Silver I'), ('Silver II', 'Silver II'), ('Silver III', 'Silver III'), ('Gold I', 'Gold I'), ('Gold II', 'Gold II'), ('Gold III', 'Gold III'), ('Platinum I', 'Platinum I'), ('Platinum II', 'Platinum II'), ('Platinum III', 'Platinum III'), ('Diamond I', 'Diamond I'), ('Diamond II', 'Diamond II'), ('Diamond III', 'Diamond III'), ('Champion I', 'Champion I'), ('Champion II', 'Champion II'), ('Champion III', 'Champion III'), ('Grand Champion I', 'Grand Champion I'), ('Grand Champion II', 'Grand Champion II'), ('Grand Champion III', 'Grand Champion III'), ('Supersonic Legend', 'Supersonic Legend')]), ('VAL', [('Iron I', 'Iron I'), ('Iron II', 'Iron II'), ('Iron III', 'Iron III'), ('Bronze I', 'Bronze I'), ('Bronze II', 'Bronze II'), ('Bronze III', 'Bronze III'), ('Silver I', 'Silver I'), ('Silver II', 'Silver II'), ('Silver III', 'Silver III'), ('Gold I', 'Gold I'), ('Gold II', 'Gold II'), ('Gold III', 'Gold III'), ('Platinum I', 'Platinum I'), ('Platinum II', 'Platinum II'), ('Platinum III', 'Platinum III'), ('Diamon I', 'Diamon I'), ('Diamond II', 'Diamond II'), ('Diamond III', 'Diamond III'), ('Ascendent I', 'Ascendent I'), ('Ascendent II', 'Ascendent II'), ('Ascendent III', 'Ascendent III'), ('Inmortal I', 'Inmortal I'), ('Inmortal II', 'Inmortal II'), ('Inmortal III', 'Inmortal III'), ('Radiant', 'Radiant')])], default='un', max_length=30),
        ),
    ]

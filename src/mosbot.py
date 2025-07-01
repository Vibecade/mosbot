from typing import Optional
import os

import discord
from discord import app_commands
import sqlite3
import re

guild_id = os.environ.get('MOSBOT_GUILD_ID')
MY_GUILD = discord.Object(id=guild_id)  # replace with your guild id
brann_idiotbeard = 1343634021799694417
ignored_ids = [473513656265736233, #Moscato
               brann_idiotbeard #Brann
              ]

ignored_list_str = repr(ignored_ids).replace('[','(').replace(']',')')

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)

con = sqlite3.connect("mosbot.db")

cur = con.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS bank(id, balance)")
con.commit()
con.close()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')



@client.tree.command()
@app_commands.describe(
    member='The user to give $mos to',
    dollars='The numbers of $mos to give',
)
async def mosgive(interaction: discord.Interaction, member: discord.Member, dollars: int, memo: str):
    valid_role = False
    caller = interaction.user
    caller_name = str(caller.display_name)

    member_name = str(member.display_name)
    member_id = member.id

    if dollars < 0:
        dollars = dollars * -1

    for role in caller.roles:
        if role.name == "mos":
            valid_role = True

    if valid_role == True:

        con = sqlite3.connect("mosbot.db")
        cur = con.cursor()
        res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))

        if res.fetchone() is not None:
            res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))
            data = res.fetchone()

            update_dollars = data[1] + dollars

            cur.execute("UPDATE bank SET balance=? WHERE id=?", (update_dollars, member_id,))
            con.commit()
            con.close()

            await interaction.response.send_message(f'{member_name} has gained {dollars} $mos, and now has {update_dollars} $mos. Memo: {memo}')

        else:
            cur.execute("INSERT INTO bank VALUES(?,?)", (member_id, dollars,))
            con.commit()
            con.close()

            await interaction.response.send_message(f'{member_name} now has {dollars} $mos. Memo: {memo}')

    else:
        await interaction.response.send_message(f'{caller_name} does not have $mos ledger write permissions.')



@client.tree.command()
@app_commands.describe(
    dollars='The numbers of $mos to steal',
)
async def mossteal(interaction: discord.Interaction, dollars: int, memo: str):
    valid_id = False
    caller = interaction.user
    caller_name = str(caller.display_name)


    # There is currently one valid criminal interaction
    #   until a table of relationships or something is made, this is hardcoded
    sovoke_id = 134554502140395520
    thonir_id = 348883795266764800

    dollars = abs(dollars)

    if caller.id == sovoke_id:
        valid_id = True

    if valid_id == True:

        con = sqlite3.connect("mosbot.db")
        cur = con.cursor()
        update_source = 0
        update_target = 0

        source_res = cur.execute("SELECT * FROM bank WHERE id=?", (thonir_id,))
        if (source_res is not None):
            source_data = source_res.fetchone()
            update_source = source_data[1] - dollars

        target_res = cur.execute("SELECT * FROM bank WHERE id=?", (sovoke_id,))
        if (target_res is not None):
            target_data = target_res.fetchone()
            update_target = target_data[1] + dollars

            # This should not run if either of the above cursors failed
        if (update_source != 0) and (update_target != 0):
            cur.execute("UPDATE bank SET balance=? WHERE id=?", (update_source, thonir_id,))
            cur.execute("UPDATE bank SET balance=? WHERE id=?", (update_target, sovoke_id,))
            con.commit()
            con.close()

            await interaction.response.send_message(f'Sovoke has stolen {dollars} $mos from Thonir, and now has {update_target} $mos. \n Thonir now has {update_source} $mos. Memo: {memo}')
    else:
        await interaction.response.send_message(f'{caller_name} does not have $mos ledger write permissions.')



@client.tree.command()
@app_commands.describe(
    member='The user to take $mos from',
    dollars='The numbers of $mos to take',
)
async def mostake(interaction: discord.Interaction, member: discord.Member, dollars: int, memo: str):
    valid_role = False
    caller = interaction.user
    caller_name = str(caller.display_name)

    member_name = str(member.display_name)
    member_id = member.id

    if dollars < 0:
        dollars = dollars * -1

    for role in caller.roles:
        if role.name == "mos":
            valid_role = True

    if member_id == brann_idiotbeard:
        valid_role = True

    if valid_role == True:

        con = sqlite3.connect("mosbot.db")
        cur = con.cursor()
        res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))

        if res.fetchone() is not None:
            res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))
            data = res.fetchone()

            update_dollars = data[1] - dollars

            cur.execute("UPDATE bank SET balance=? WHERE id=?", (update_dollars, member_id,))
            con.commit()
            con.close()

            await interaction.response.send_message(f'{member_name} has lost {dollars} $mos, and now has {update_dollars} $mos. Memo: {memo}')

        else:
            init_dollars = 0 - dollars
            cur.execute("INSERT INTO bank VALUES(?,?)", (member_id, init_dollars,))
            con.commit()
            con.close()

            await interaction.response.send_message(f'{member_name} has lost {dollars} $mos, and now has {init_dollars} $mos. Memo: {memo}')

    else:
        await interaction.response.send_message(f'{caller_name} does not have $mos ledger write permissions.')

@client.tree.command()
@app_commands.describe(
    members='The users to give $mos to (mention them with @)',
    dollars='The numbers of $mos to give to each user',
    memo='A memo for the transaction'
)
async def mosbulkgive(interaction: discord.Interaction, members: str, dollars: int, memo: str):
    valid_role = False
    caller = interaction.user
    caller_name = str(caller.display_name)

    if dollars < 0:
        dollars = dollars * -1

    # Check if caller has the "mos" role
    for role in caller.roles:
        if role.name == "mos":
            valid_role = True

    if not valid_role:
        await interaction.response.send_message(f'{caller_name} does not have $mos ledger write permissions.')
        return

    # Parse mentioned users from the members string
    mentioned_users = []
    member_ids = []
    
    # Extract user IDs from mentions (format: <@!123456789> or <@123456789>)
    user_mentions = re.findall(r'<@!?(\d+)>', members)
    
    if not user_mentions:
        await interaction.response.send_message('No valid user mentions found. Please mention users with @username.')
        return

    # Get member objects from IDs
    guild = interaction.guild
    for user_id in user_mentions:
        try:
            member = guild.get_member(int(user_id))
            if member:
                mentioned_users.append(member)
                member_ids.append(int(user_id))
        except:
            continue

    if not mentioned_users:
        await interaction.response.send_message('No valid users found from the mentions.')
        return

    # Process each user
    con = sqlite3.connect("mosbot.db")
    cur = con.cursor()
    
    results = []
    successful_transactions = 0
    
    for member in mentioned_users:
        member_name = str(member.display_name)
        member_id = member.id
        
        try:
            res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))
            
            if res.fetchone() is not None:
                res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))
                data = res.fetchone()
                
                update_dollars = data[1] + dollars
                
                cur.execute("UPDATE bank SET balance=? WHERE id=?", (update_dollars, member_id,))
                results.append(f'✅ {member_name}: {dollars} $mos (now has {update_dollars} $mos)')
                successful_transactions += 1
            else:
                cur.execute("INSERT INTO bank VALUES(?,?)", (member_id, dollars,))
                results.append(f'✅ {member_name}: {dollars} $mos (new account)')
                successful_transactions += 1
                
        except Exception as e:
            results.append(f'❌ {member_name}: Failed to process transaction')
    
    con.commit()
    con.close()
    
    # Create response message
    response_msg = f'**Bulk $mos Distribution Complete**\n'
    response_msg += f'Successfully processed {successful_transactions}/{len(mentioned_users)} transactions\n'
    response_msg += f'Amount per user: {dollars} $mos\n'
    response_msg += f'Memo: {memo}\n\n'
    response_msg += '**Results:**\n' + '\n'.join(results)
    
    await interaction.response.send_message(response_msg)

@client.tree.command()
@app_commands.describe(
    member='The user to check $mos balance'
)
async def moscheck(interaction: discord.Interaction, member: discord.Member):
    """Checks a user's current $mos balance"""
    member_name = str(member.display_name)
    member_id = member.id

    con = sqlite3.connect("mosbot.db")
    cur = con.cursor()
    res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))

    if res.fetchone() is not None:
        res = cur.execute("SELECT * FROM bank WHERE id=?", (member_id,))
        data = res.fetchone()
        con.close()

        await interaction.response.send_message(f'{member_name} has {data[1]} $mos')

    else:
        con.close()

        await interaction.response.send_message(f'{member_name} has 0 $mos')

@client.tree.command()
@app_commands.describe(
)
async def mosrank(interaction: discord.Interaction):
    """Displays current top 10 $mos rankings"""
    con = sqlite3.connect("mosbot.db")
    cur = con.cursor()

    #Get only top 10 values
    res = cur.execute("SELECT * FROM bank WHERE id NOT IN %s ORDER BY balance DESC limit 10" % ignored_list_str)
    data = res.fetchall()
    con.close()

    user_rank = []
    user_id = []

    # Build both lists out of our result
    for data_result in data:
        user_id.append(data_result[0])
        user_rank.append(data_result[1])

    guild = await client.fetch_guild(guild_id)

    # Get a list of all members corresponding to ids from the result
    members_by_id = await guild.query_members(limit=10,user_ids=user_id)
    member_dict = dict(map(lambda key: (key.id,key.display_name),members_by_id))


    rank_str = f"Top 10 $mos balance\n"
    for num,id,amnt in zip(range(1,11),user_id,user_rank):
        rank_str += f"{num}. {member_dict[id]}: {amnt} $mos \n"

    await interaction.response.send_message(rank_str)

@client.tree.command()
@app_commands.describe(
)
async def mosdebt(interaction: discord.Interaction):
    """Displays current bottom 10 $mos rankings"""
    con = sqlite3.connect("mosbot.db")
    cur = con.cursor()


    # does this work to make a list for sqlite

    #Get bottom 10 values and filter out ignored ids
    res = cur.execute("SELECT * FROM bank WHERE id NOT IN %s ORDER BY balance ASC limit 10" % ignored_list_str)
    data = res.fetchall()
    con.close()

    user_rank = []
    user_id = []

    # Build both lists out of our result
    for data_result in data:
        user_id.append(data_result[0])
        user_rank.append(data_result[1])

    guild = await client.fetch_guild(guild_id)

    # Get a list of all members corresponding to ids from the result
    members_by_id = await guild.query_members(limit=10,user_ids=user_id)
    member_dict = dict(map(lambda key: (key.id,key.display_name),members_by_id))


    rank_str = f"Bottom 10 $mos balance\n"
    for num,id,amnt in zip(range(1,11),user_id,user_rank):
        rank_str += f"{num}. {member_dict[id]}: {amnt} $mos \n"

    await interaction.response.send_message(rank_str)



client.run(os.environ.get('MOSBOT_TOKEN'))
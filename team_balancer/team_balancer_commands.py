from discord.ext import commands
from team_balancer.team_balancer import TeamBalancer


class TeamBalancerCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='start-balance',
        brief="Start a new custom game to balance."
    )
    async def start_balance(self, ctx, game_mode=None):
        gamemode = "aram" if game_mode and game_mode.lower() == "aram" else "sr"
        if game_mode and game_mode.lower() == "aram":
            self.team_balancer = TeamBalancer(gamemode)
        else:
            self.team_balancer = TeamBalancer(gamemode)

        msg = f"Starting a new balanced {gamemode} custom game. \n"
        msg += "Please use !add-player to enter your summoner name, without spaces"
        if gamemode == "sr":
            msg += ", followed by any roles you **DON'T** want to play."
        else:
            msg += "."

        await ctx.send(msg)

    @commands.command(
        name='add-player',
        brief="Add a player to the game."
    )
    async def join_game(self, ctx, summoner_name, *roles):
        fixed_roles = set()
        for role in roles:
            if "top" in role.lower() or "tp" in role.lower():
                fixed_roles.add("top")
            elif "jg" in role.lower() or "jng" in role.lower() or "jung" in role.lower():
                fixed_roles.add("jg")
            elif "mid" in role.lower():
                fixed_roles.add("mid")
            elif "bot" in role.lower() or "ad" in role.lower():
                fixed_roles.add("bot")
            elif "sup" in role.lower():
                fixed_roles.add("supp")

        if self.team_balancer.add_player(summoner_name, fixed_roles):
            num_players = self.team_balancer.get_num_players()
            await ctx.send(f"{summoner_name} has joined the game. {num_players} are in the game.")

            if num_players == 10:
                await ctx.send("Game is full, starting balance.")
                await self.compute_team(ctx)
        else:
            await ctx.send(f"{summoner_name} is already in the game.")

    @commands.command(
        name='compute-team',
        aliases=['balance', 'balance-teams'],
        brief="Compute the best teams for the set of players."
    )
    async def compute_team(self, ctx):
        num_players = self.team_balancer.get_num_players()
        gamemode = self.team_balancer.gamemode
        if num_players < 6 and gamemode == "aram" \
                or gamemode == "sr" and num_players % 2 == 1 and num_players < 8:

            await ctx.send("Not enough players to balance.")
            return

        teams = self.team_balancer.balance()
        await ctx.send(self._teams_to_msg(teams))

    @commands.command(
        name='reroll', brief="Choose a new best team."
    )
    async def reroll(self, ctx):
        teams = self.team_balancer.reroll()
        if isinstance(teams, str):
            await ctx.send(teams)
        else:
            msg = "New teams: \n" + self._teams_to_msg(teams)
            await ctx.send(msg)

    def _teams_to_msg(self, teams):
        msg = ""
        if self.team_balancer.gamemode == "aram":
            msg = "Team 1: \n"
            for player in teams[0]:
                msg += f"{player}\n"

            msg += "\nTeam 2: \n"
            for player in teams[1]:
                msg += f"{player}\n"
        else:
            msg = "Team 1: \n"
            for (player, role) in teams[0]:
                msg += f"{role}: {player}\n"

            msg += "\nTeam 2: \n"
            for (player, role) in teams[1]:
                msg += f"{role}: {player}\n"

        msg += f"(Skill gap = {teams[2]})"

        return msg

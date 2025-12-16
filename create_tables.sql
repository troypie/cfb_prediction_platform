
-- Team stats table create script
CREATE TABLE team_season_stats (
    -- Primary Identifiers
    "team" VARCHAR(100) NOT NULL,
    "season" INTEGER NOT NULL,
    "conference" VARCHAR(100),

    -- General Game Stats
    "games" INTEGER DEFAULT 0,
    "possessionTime" INTEGER DEFAULT 0,
    "possessionTimeOpponent" INTEGER DEFAULT 0,
    "turnovers" INTEGER DEFAULT 0,
    "turnoversOpponent" INTEGER DEFAULT 0,
    "totalYards" INTEGER DEFAULT 0,
    "totalYardsOpponent" INTEGER DEFAULT 0,
    "penalties" INTEGER DEFAULT 0,
    "penaltiesOpponent" INTEGER DEFAULT 0,
    "penaltyYards" INTEGER DEFAULT 0,
    "penaltyYardsOpponent" INTEGER DEFAULT 0,

    -- First Downs
    "firstDowns" INTEGER DEFAULT 0,
    "firstDownsOpponent" INTEGER DEFAULT 0,

    -- Third & Fourth Downs
    "thirdDowns" INTEGER DEFAULT 0,
    "thirdDownsOpponent" INTEGER DEFAULT 0,
    "thirdDownConversions" INTEGER DEFAULT 0,
    "thirdDownConversionsOpponent" INTEGER DEFAULT 0,
    "fourthDowns" INTEGER DEFAULT 0,
    "fourthDownsOpponent" INTEGER DEFAULT 0,
    "fourthDownConversions" INTEGER DEFAULT 0,
    "fourthDownConversionsOpponent" INTEGER DEFAULT 0,

    -- Passing
    "passAttempts" INTEGER DEFAULT 0,
    "passAttemptsOpponent" INTEGER DEFAULT 0,
    "passCompletions" INTEGER DEFAULT 0,
    "passCompletionsOpponent" INTEGER DEFAULT 0,
    "netPassingYards" INTEGER DEFAULT 0,
    "netPassingYardsOpponent" INTEGER DEFAULT 0,
    "passingTDs" INTEGER DEFAULT 0,
    "passingTDsOpponent" INTEGER DEFAULT 0,
    "passesIntercepted" INTEGER DEFAULT 0,
    "passesInterceptedOpponent" INTEGER DEFAULT 0,

    -- Rushing
    "rushingAttempts" INTEGER DEFAULT 0,
    "rushingAttemptsOpponent" INTEGER DEFAULT 0,
    "rushingYards" INTEGER DEFAULT 0,
    "rushingYardsOpponent" INTEGER DEFAULT 0,
    "rushingTDs" INTEGER DEFAULT 0,
    "rushingTDsOpponent" INTEGER DEFAULT 0,

    -- Defense Specific
    "sacks" INTEGER DEFAULT 0,
    "sacksOpponent" INTEGER DEFAULT 0,
    "tacklesForLoss" INTEGER DEFAULT 0,
    "tacklesForLossOpponent" INTEGER DEFAULT 0,
    "interceptions" INTEGER DEFAULT 0,
    "interceptionsOpponent" INTEGER DEFAULT 0,
    "interceptionYards" INTEGER DEFAULT 0,
    "interceptionYardsOpponent" INTEGER DEFAULT 0,
    "interceptionTDs" INTEGER DEFAULT 0,
    "interceptionTDsOpponent" INTEGER DEFAULT 0,

    -- Fumbles
    "fumblesLost" INTEGER DEFAULT 0,
    "fumblesLostOpponent" INTEGER DEFAULT 0,
    "fumblesRecovered" INTEGER DEFAULT 0,
    "fumblesRecoveredOpponent" INTEGER DEFAULT 0,

    -- Special Teams (Returns)
    "kickReturns" INTEGER DEFAULT 0,
    "kickReturnsOpponent" INTEGER DEFAULT 0,
    "kickReturnYards" INTEGER DEFAULT 0,
    "kickReturnYardsOpponent" INTEGER DEFAULT 0,
    "kickReturnTDs" INTEGER DEFAULT 0,
    "kickReturnTDsOpponent" INTEGER DEFAULT 0,
    "puntReturns" INTEGER DEFAULT 0,
    "puntReturnsOpponent" INTEGER DEFAULT 0,
    "puntReturnYards" INTEGER DEFAULT 0,
    "puntReturnYardsOpponent" INTEGER DEFAULT 0,
    "puntReturnTDs" INTEGER DEFAULT 0,
    "puntReturnTDsOpponent" INTEGER DEFAULT 0,

    -- Constraint to prevent duplicate team entries per season
    PRIMARY KEY ("team", "season")
);
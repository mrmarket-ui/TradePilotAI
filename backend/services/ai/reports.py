from datetime import datetime


def build_report(stats, risk):

    return {

        "generated_at": datetime.utcnow(),

        "summary": {

            "total_trades": stats["total_trades"],

            "win_rate": stats["win_rate"],

            "profit_factor": stats["profit_factor"],

            "net_profit": stats["net_profit"],

            "drawdown": risk["maximum_drawdown"]

        }

    }

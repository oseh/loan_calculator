import cmd2
import argparse
from loan_calculator.interest_calculations import daily_interest_data, total_interest
from loan_calculator.data_store import save_calculation, get_calculation, list_calculations, CalculationData
from loguru import logger
from tabulate import tabulate
from datetime import datetime

class LoanCalculator(cmd2.Cmd):
    intro = "Welcome to the Enhanced Loan Calculator. Type help or ? to list commands.\n"
    prompt = "loan_calc> "

    calculate_parser = argparse.ArgumentParser()
    calculate_parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    calculate_parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    calculate_parser.add_argument("amount", type=float, help="Loan amount")
    calculate_parser.add_argument("currency", type=str, help="Currency code (e.g., USD)")
    calculate_parser.add_argument("base_rate", type=float, help="Base interest rate (%)")
    calculate_parser.add_argument("margin", type=float, help="Margin (%)")
    calculate_parser.add_argument("--exclude_weekends", action="store_true", help="Exclude weekends from calculation")
    calculate_parser.add_argument("--method", choices=["simple", "compound"], default="simple", help="Interest calculation method")

    @cmd2.with_argparser(calculate_parser)
    def do_calculate(self, args):
        """Calculate loan interest with parameters:
        
        start_date end_date amount currency base_rate margin [--exclude_weekends] [--method {simple,compound}]
        
        Example:
            calculate 2024-01-01 2024-02-01 10000 USD 5.0 2.0 --exclude_weekends --method simple
        """
        try:
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
            if end_date <= start_date:
                self.perror("End date must be after start date.")
                return

            calc_data = CalculationData(
                start_date=args.start_date,
                end_date=args.end_date,
                amount=args.amount,
                currency=args.currency.upper(),
                base_rate=args.base_rate,
                margin=args.margin,
                exclude_weekends=args.exclude_weekends,
                method=args.method
            )

            calc_id = save_calculation(calc_data)
            self.pfeedback(f"Calculation saved with ID: {calc_id}")
            self.do_show(str(calc_id))
            details = daily_interest_data(calc_data)
            if not details:
                self.pwarning("No interest calculated. Check your dates.")
                return

        except ValueError as ve:
            self.perror(f"Date format error: {ve}")
        except Exception as e:
            logger.error(f"Error in calculate: {str(e)}")
            self.perror(f"An error occurred: {str(e)}")

    show_parser = argparse.ArgumentParser()
    show_parser.add_argument("calculation_id", type=int, help="ID of the calculation to show")

    @cmd2.with_argparser(show_parser)
    def do_show(self, args):
        """Show calculation details by ID.

        Usage:
            show <calculation_id>
        """
        try:
            calc = get_calculation(args.calculation_id)
            if not calc:
                self.perror("Calculation not found.")
                return

            details = daily_interest_data(calc)
            if not details:
                self.pwarning("No interest calculated. Check your dates.")
                return

            headers = ["Accrual Date", "Daily Interest (No Margin)", "Daily Interest (With Margin)", "Days Elapsed"]
            table = [
                [
                    d["Accrual Date"],
                    f"{d['Daily Interest (No Margin)']:.2f}",
                    f"{d['Daily Interest (With Margin)']:.2f}",
                    d["Days Elapsed"]
                ] for d in details
            ]

            self.poutput(tabulate(table, headers, tablefmt="fancy_grid"))
            total = total_interest(calc)
            self.poutput(f"\nTotal Interest: {total:.2f} {calc.currency}")

        except Exception as e:
            logger.error(f"Error in show: {str(e)}")
            self.perror(f"An error occurred: {str(e)}")

    def do_list(self, args):
        """List all saved calculations."""
        try:
            all_calcs = list_calculations()
            if not all_calcs:
                self.perror("No calculations found.")
                return

            headers = ["ID", "Start Date", "End Date", "Amount", "Currency", "Base Rate (%)", "Margin (%)", "Exclude Weekends", "Method"]
            table = [
                [
                    cid,
                    calc.start_date,
                    calc.end_date,
                    f"{calc.amount:.2f}",
                    calc.currency,
                    f"{calc.base_rate:.2f}",
                    f"{calc.margin:.2f}",
                    calc.exclude_weekends,
                    calc.method.capitalize()
                ] for cid, calc in all_calcs
            ]
            self.poutput(tabulate(table, headers, tablefmt="fancy_grid"))

        except Exception as e:
            logger.error(f"Error in list: {str(e)}")
            self.perror(f"An error occurred: {str(e)}")

    update_parser = argparse.ArgumentParser()
    update_parser.add_argument("calculation_id", type=int, help="ID of the calculation to update")
    update_parser.add_argument("start_date", type=str, help="Start date in YYYY-MM-DD format")
    update_parser.add_argument("end_date", type=str, help="End date in YYYY-MM-DD format")
    update_parser.add_argument("amount", type=float, help="Loan amount")
    update_parser.add_argument("currency", type=str, help="Currency code (e.g., USD)")
    update_parser.add_argument("base_rate", type=float, help="Base interest rate (%)")
    update_parser.add_argument("margin", type=float, help="Margin (%)")
    update_parser.add_argument("--exclude_weekends", action="store_true", help="Exclude weekends from calculation")
    update_parser.add_argument("--method", choices=["simple", "compound"], default="simple", help="Interest calculation method")

    @cmd2.with_argparser(update_parser)
    def do_update(self, args):
        """Update an existing calculation with parameters:
        
        calculation_id start_date end_date amount currency base_rate margin [--exclude_weekends] [--method {simple,compound}]
        
        Example:
            update 1 2024-01-01 2024-02-01 10000 USD 5.0 2.0 --exclude_weekends --method compound
        """
        try:
            # Validate date formats
            start_date = datetime.strptime(args.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(args.end_date, "%Y-%m-%d")
            if end_date <= start_date:
                self.perror("End date must be after start date.")
                return

            existing_calc = get_calculation(args.calculation_id)
            if not existing_calc:
                self.perror("Calculation not found.")
                return

            updated_calc = CalculationData(
                start_date=args.start_date,
                end_date=args.end_date,
                amount=args.amount,
                currency=args.currency.upper(),
                base_rate=args.base_rate,
                margin=args.margin,
                exclude_weekends=args.exclude_weekends,
                method=args.method
            )

            save_calculation(updated_calc, args.calculation_id)
            self.pfeedback(f"Calculation with ID {args.calculation_id} updated.")
            self.do_show(str(args.calculation_id))
            details = daily_interest_data(updated_calc)
            if not details:
                self.pwarning("No interest calculated. Check your dates.")
                return

        except ValueError as ve:
            self.perror(f"Date format error: {ve}")
        except Exception as e:
            logger.error(f"Error in update: {str(e)}")
            self.perror(f"An error occurred: {str(e)}")

    def do_quit(self, args):
        """Quit the application."""
        self.poutput("Thank you for using the Loan Calculator. Goodbye!")
        return True

    # Adding alias for 'exit'
    do_exit = do_quit

    def do_help(self, args):
        """Provide detailed help with examples."""
        if args:
            # If specific command help is requested
            super().do_help(args)
        else:
            self.poutput("Loan Calculator Commands:\n")
            self.poutput("  calculate    Calculate loan interest with specified parameters.")
            self.poutput("  show         Show details of a specific calculation by ID.")
            self.poutput("  list         List all saved calculations.")
            self.poutput("  update       Update an existing calculation.")
            self.poutput("  quit/exit    Exit the application.\n")
            self.poutput("Type 'help <command>' for more details on each command.")


app = LoanCalculator()
app.cmdloop()
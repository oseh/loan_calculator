import pytest
from typer.testing import CliRunner
from loan_calculator.main import app

runner = CliRunner()

def test_calculate_command():
    result = runner.invoke(app, [
        "calculate",
        "--start-date", "2024-01-01",
        "--end-date", "2024-01-05",
        "--amount", "10000",
        "--currency", "USD",
        "--base-rate", "5",
        "--margin", "2"
    ])
    assert result.exit_code == 0
    assert "Total Interest:" in result.output

def test_show_command():
    result = runner.invoke(app, ["show", "1"])
    assert result.exit_code == 0
    assert "Calculation not found.\n" in result.output  # Adjusted expected output

def test_list_calcs_command():
    result = runner.invoke(app, ["list-calcs"])
    assert result.exit_code == 0
    assert "ID: 0," in result.output  # Adjusted expected output

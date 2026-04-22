import asyncio
import time
from llm_guard.vault import Vault
from llm_guard.output_scanners import (
    BanSubstrings,
    BanTopics,
    Code,
    Deanonymize,
    Gibberish,
    Language,
    NoRefusal,
    Relevance,
    Sensitive,
    Sentiment,
    Toxicity,
)
# Inicjalizacja Vault
vault = Vault()

async def run_output_scanner_tests():
    # Przykładowy prompt, który mógł wygenerować te odpowiedzi
    sample_prompt = "Tell me something about this person and provide some code."
    
    # Lista testów: (Nazwa, Instancja skanera, Odpowiedź modelu do przetestowania)
    scanners = [
        ("Toxicity", Toxicity(threshold=0.5), "I am a helpful assistant but you are being very rude!"),
        ("Deanonymize", Deanonymize(vault), "The person you asked about is [REDACTED]."),
        ("BanSubstrings", BanSubstrings(substrings=["internal_api_v1"]), "Error: internal_api_v1 failed."),
        ("BanTopics", BanTopics(topics=["politics"], threshold=0.6), "In the last election, the candidate..."),
        ("Code", Code(languages=["Python"]), "Here is your code: \nprint('Hello World')"),
        ("Gibberish", Gibberish(threshold=0.7), "kjhgsdf 876234 khgsdf"),
        ("Language", Language(valid_languages=["en"]), "To jest odpowiedź po polsku."),
        ("NoRefusal", NoRefusal(threshold=0.5), "I'm sorry, I cannot fulfill this request."),
        ("Relevance", Relevance(threshold=0.5), "The weather is nice today."), 
        ("Sensitive", Sensitive(entity_types=["PHONE_NUMBER"]), "My phone number is 555-0199."),
        ("Sentiment", Sentiment(threshold=-0.5), "This is the worst possible outcome and I hate it."),
    ]

    header = f"{'Output Scanner':<20} | {'Is Valid':<10} | {'Risk Score':<10} | {'Time (ms)':<10} | {'Sanitized Output'}"
    separator = "-" * 135
    
    print(header)
    print(separator)

    with open("output_scanner_results.txt", "w", encoding="utf-8") as f:
        f.write(header + "\n")
        f.write(separator + "\n")

        for name, scanner, model_output in scanners:
            try:
                start_time = time.perf_counter()
                
                # Output skanery zazwyczaj przyjmują (prompt, model_output)
                # Niektóre skanery mogą mieć specyficzne wymagania, ale standard to (prompt, output)
                sanitized_output, is_valid, risk_score = scanner.scan(sample_prompt, model_output)
                
                end_time = time.perf_counter()
                execution_time_ms = (end_time - start_time) * 1000
                
                clean_txt = sanitized_output.replace("\n", " ")
                display_output = clean_txt[:45] + "..." if len(clean_txt) > 45 else clean_txt
                
                row = f"{name:<20} | {str(is_valid):<10} | {risk_score:<10.2f} | {execution_time_ms:<10.2f} | {display_output}"
                
                print(row)
                f.write(row + "\n")
                
            except Exception as e:
                error_msg = f"{name:<20} | ERROR: {str(e)}"
                print(error_msg)
                f.write(error_msg + "\n")

    print(f"\nWyniki skanerów wyjściowych zapisano do: output_scanner_results.txt")

if __name__ == "__main__":
    asyncio.run(run_output_scanner_tests())
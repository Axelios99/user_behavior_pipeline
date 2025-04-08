from pipeline import load_data_to_process  # o desde donde la tengas definida
from utils import setup_logger

if __name__ == "__main__":

    prints, taps, pays = load_data_to_process()

    print("✅ Prints headers:")
    print(prints.columns)
    print("✅ Prints data:")
    print(prints.head())
    print(f"📄 Total de prints cargados: {len(prints)}\n")

    print("✅ Taps headers:")
    print(taps.columns)
    print("✅ Taps data:")
    print(taps.head())
    print(f"📄 Total de taps cargados: {len(taps)}\n")

    print("✅ Pays:")
    print(pays.columns)
    print("✅ Pays data:")
    print(pays.head())
    print(f"📄 Total de pays cargados: {len(pays)}")

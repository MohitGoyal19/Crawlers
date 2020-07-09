import pandas as pd

def main():
    df = pd.read_csv('items_jnbk_2.csv')

    frames = dict()

    for x in range(len(df)):
        maker = df.loc[x]['Maker']
        if not maker in frames.keys():
            frames[maker] = pd.DataFrame(columns=df.columns)
        frames[maker].loc[len(frames[maker])] = df.loc[x]
        print(x, 'out of', len(df))

    for key, value in frames.items():
        value.to_excel('jnbk/'+key+'.xlsx', headers=None)

    return


if __name__ == '__main__':
    main()

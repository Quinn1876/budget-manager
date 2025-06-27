import { getClient } from "@/lib/client";
import { gql } from "@apollo/client";

const query = gql`
  query GetAllAccounts {
    listAccounts {
      account_number
      account_type
      owner
      account_name
    }
}`;

export default async function Home() {
  const { data } = await getClient().query({ query });
  return (
    <div>
      <table>
        <tbody>
            {data["listAccounts"].map((item: {account_number: string}) => {
              return (
                <tr key={item.account_number}>
                  <td >{item.account_number}</td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
}

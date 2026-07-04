
package labs.SocketProgramming.Client;

import java.net.*;
import java.io.*;

public class MyClient {
    public static void main(String[] args) throws Exception {
        // Create Socket connecting to Server 
        Socket s = new Socket("127.0.0.1", 5555);
        System.out.println("Connected to Server, Please type your message and hit Enter to send");

        // Input/Output streams 
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        OutputStream ostream = s.getOutputStream();
        PrintWriter pw = new PrintWriter(ostream, true);
        InputStream istream = s.getInputStream();
        BufferedReader receive = new BufferedReader(new InputStreamReader(istream));

        String clientMessage = "", serverMessage = "";
        while (true) {
            // Send input to server 
            System.out.print("Client: ");
            clientMessage = br.readLine();
            pw.println(clientMessage);
            if (clientMessage.equals("bye")) break;

            // Read server message 
            serverMessage = receive.readLine();
            System.out.println("Server: " + serverMessage);
            if (serverMessage.equals("bye")) break;
        }
        
        // Closing connections 
        s.close();
        istream.close();
        ostream.close();
        System.out.println("Connection Terminated");
    }
}

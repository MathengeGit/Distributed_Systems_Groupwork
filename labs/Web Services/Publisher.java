import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;
import java.io.*;
import java.net.InetSocketAddress;
import java.util.regex.*;

public class Publisher {

    static final String WSDL =
        "<?xml version=\"1.0\"?>\n" +
        "<definitions name=\"CalculatorService\" xmlns=\"http://schemas.xmlsoap.org/wsdl/\">\n" +
        "  <message name=\"addRequest\"><part name=\"a\" type=\"xsd:int\"/><part name=\"b\" type=\"xsd:int\"/></message>\n" +
        "  <message name=\"addResponse\"><part name=\"result\" type=\"xsd:int\"/></message>\n" +
        "  <portType name=\"CalculatorPortType\">\n" +
        "    <operation name=\"add\">\n" +
        "      <input message=\"tns:addRequest\"/>\n" +
        "      <output message=\"tns:addResponse\"/>\n" +
        "    </operation>\n" +
        "    <operation name=\"subtract\"/>\n" +
        "    <operation name=\"multiply\"/>\n" +
        "  </portType>\n" +
        "  <service name=\"CalculatorService\">\n" +
        "    <documentation>Simple SOAP-style calculator web service</documentation>\n" +
        "  </service>\n" +
        "</definitions>";

    public static void main(String[] args) throws Exception {
        CalculatorService calc = new CalculatorService();
        HttpServer server = HttpServer.create(new InetSocketAddress(9999), 0);

        server.createContext("/ws/calculator", new HttpHandler() {
            @Override
            public void handle(HttpExchange exchange) throws IOException {
                String query = exchange.getRequestURI().getQuery();

                // Serve the WSDL on a GET ?wsdl request
                if ("GET".equalsIgnoreCase(exchange.getRequestMethod())
                        && query != null && query.contains("wsdl")) {
                    byte[] resp = WSDL.getBytes("UTF-8");
                    exchange.getResponseHeaders().add("Content-Type", "text/xml");
                    exchange.sendResponseHeaders(200, resp.length);
                    try (OutputStream os = exchange.getResponseBody()) { os.write(resp); }
                    return;
                }

                // Handle the SOAP-style POST request
                if ("POST".equalsIgnoreCase(exchange.getRequestMethod())) {
                    String body = new String(exchange.getRequestBody().readAllBytes(), "UTF-8");

                    String operation = extract(body, "ws:(\\w+)>");
                    int a = Integer.parseInt(extract(body, "<a>(-?\\d+)</a>"));
                    int b = Integer.parseInt(extract(body, "<b>(-?\\d+)</b>"));

                    int result;
                    switch (operation) {
                        case "add": result = calc.add(a, b); break;
                        case "subtract": result = calc.subtract(a, b); break;
                        case "multiply": result = calc.multiply(a, b); break;
                        default: throw new IllegalArgumentException("Unknown operation: " + operation);
                    }

                    String soapResponse =
                        "<?xml version=\"1.0\"?>" +
                        "<soapenv:Envelope xmlns:soapenv=\"http://schemas.xmlsoap.org/soap/envelope/\">" +
                        "<soapenv:Body>" +
                        "<ws:" + operation + "Response xmlns:ws=\"http://ws.learn.com/\">" +
                        "<result>" + result + "</result>" +
                        "</ws:" + operation + "Response>" +
                        "</soapenv:Body>" +
                        "</soapenv:Envelope>";

                    byte[] resp = soapResponse.getBytes("UTF-8");
                    exchange.getResponseHeaders().add("Content-Type", "text/xml");
                    exchange.sendResponseHeaders(200, resp.length);
                    try (OutputStream os = exchange.getResponseBody()) { os.write(resp); }
                    return;
                }

                exchange.sendResponseHeaders(405, -1);
            }

            String extract(String body, String pattern) {
                Matcher m = Pattern.compile(pattern).matcher(body);
                if (m.find()) return m.group(1);
                throw new RuntimeException("Could not parse: " + pattern);
            }
        });

        server.setExecutor(null);
        server.start();
        System.out.println("Web service published at: http://localhost:9999/ws/calculator");
        System.out.println("WSDL available at:        http://localhost:9999/ws/calculator?wsdl");
    }
}
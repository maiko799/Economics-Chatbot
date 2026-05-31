import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from flask import Flask, request, jsonify

nltk.download('punkt')

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

stemmer = PorterStemmer()
stop_words = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'as', 'at',
    'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both', 'but', 'by', 'could', 'did', 'do',
    'does', 'doing', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'has', 'have', 'having',
    'he', 'her', 'here', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'i', 'if', 'in', 'into', 'is', 'it',
    'its', 'itself', 'just', 'me', 'more', 'most', 'my', 'myself', 'no', 'nor', 'not', 'now', 'of', 'off', 'on',
    'once', 'only', 'or', 'other', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'she', 'should',
    'so', 'some', 'such', 'than', 'that', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
    'these', 'they', 'this', 'those', 'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'we',
    'were', 'what', 'when', 'where', 'which', 'while', 'who', 'whom', 'why', 'with', 'would', 'you', 'your',
    'yours', 'yourself', 'yourselves'
}

# Economics reference data
topics = {
    'gdp': {
        'definition': 'Gross Domestic Product measures the total value of all final goods and services produced within a country over a specific time period.',
        'importance': 'It is the most common way economists track how large an economy is and whether it is growing or shrinking.',
        'example': 'For example, if GDP rises, it usually means businesses are producing more and people are spending more, which signals economic expansion.'
    },
    'inflation': {
        'definition': 'Inflation is a general rise in the price level across the economy, which means each unit of currency buys less than before.',
        'importance': 'Understanding inflation helps people see how savings, wages, and interest rates change over time.',
        'example': 'A common example is when grocery prices increase year after year, so the same amount of money buys fewer goods than before.'
    },
    'unemployment': {
        'definition': 'Unemployment occurs when people who are available and willing to work cannot find jobs.',
        'importance': 'High unemployment is a sign of slack in the economy and can reduce living standards and consumer spending.',
        'example': 'During a recession, many workers may lose jobs because firms cut production, causing unemployment to rise.'
    },
    'monetary policy': {
        'definition': 'Monetary policy is how a central bank uses tools like interest rates and money supply to influence economic activity.',
        'importance': 'It is used to stabilize inflation and support growth without causing too much price pressure.',
        'example': 'If inflation is too high, the central bank might raise interest rates so borrowing becomes more expensive and spending slows.'
    },
    'fiscal policy': {
        'definition': 'Fiscal policy is the government’s use of spending and taxation to influence aggregate demand and economic performance.',
        'importance': 'It can be used to boost the economy during recessions or cool it down when inflation is too high.',
        'example': 'During a downturn, the government may increase infrastructure spending to create jobs and support demand.'
    },
    'aggregate demand': {
        'definition': 'Aggregate demand is the total demand for goods and services in an economy at a given overall price level and time.',
        'importance': 'It shows whether consumers, businesses, and governments are buying enough to sustain growth.',
        'example': 'When consumers feel confident, aggregate demand rises and businesses may produce more to meet higher spending.'
    },
    'aggregate supply': {
        'definition': 'Aggregate supply is the total quantity of goods and services firms are willing to produce at different price levels.',
        'importance': 'Shifts in aggregate supply help explain inflationary pressures and output changes.',
        'example': 'A new technology that reduces production costs can shift aggregate supply to the right, allowing more output at lower prices.'
    },
    'supply and demand': {
        'definition': 'Supply and demand is the basic economics model that explains how prices and quantities are determined in markets.',
        'importance': 'It helps describe why shortages and surpluses form and how markets move toward equilibrium.',
        'example': 'If demand for electric cars rises while supply stays the same, the price tends to increase until supply catches up.'
    },
    'elasticity': {
        'definition': 'Elasticity measures how much buyers or sellers respond to a change in price, income, or other factors.',
        'importance': 'It tells us whether consumers are sensitive to price changes and how firms should set prices.',
        'example': 'Gasoline demand tends to be inelastic, so price increases do not dramatically reduce consumption in the short term.'
    },
    'utility maximization': {
        'definition': 'Utility maximization is the idea that consumers choose a bundle of goods to get the most satisfaction within their budget.',
        'importance': 'This concept explains demand and how people make trade-offs between goods.',
        'example': 'A student may choose between buying a textbook or taking a tutoring session based on which option gives more value for their money.'
    },
    'opportunity cost': {
        'definition': 'Opportunity cost is the value of the next best alternative foregone when making a choice.',
        'importance': 'It reminds us that every decision has a cost, even when there is no money changing hands.',
        'example': 'If you spend time studying instead of working, the opportunity cost is the wages you could have earned.'
    },
    'ppf': {
        'definition': 'The Production Possibility Frontier shows the maximum combinations of two goods an economy can produce with limited resources.',
        'importance': 'It illustrates scarcity, efficiency, and the trade-offs of allocating resources.',
        'example': 'A country may choose between producing more food or more electronics, but not both at maximum levels without more resources.'
    },
    'game theory': {
        'definition': 'Game theory studies how people or firms make decisions when the outcome depends on the choices of others.',
        'importance': 'It helps explain strategic behavior in markets, negotiations, and competition.',
        'example': 'Airlines often use game theory when deciding whether to match a competitor’s price cut or keep fares unchanged.'
    },
    'perfect competition': {
        'definition': 'Perfect competition describes a market with many buyers and sellers, identical products, and no barriers to entry.',
        'importance': 'It is a theoretical benchmark that shows how prices would behave in a highly competitive market.',
        'example': 'Agricultural markets come closest to perfect competition because many farmers sell similar goods at market prices.'
    },
    'monopoly': {
        'definition': 'A monopoly is a market dominated by one seller with no close substitutes, allowing the firm to set price above marginal cost.',
        'importance': 'Monopolies can reduce consumer welfare and are often regulated or broken up by policymakers.',
        'example': 'A utility company with exclusive control of electricity in a region is a classic monopoly.'
    },
    'oligopoly': {
        'definition': 'An oligopoly is a market with a few large firms that may compete or cooperate on price and output decisions.',
        'importance': 'It explains industries where a small number of firms have significant market power.',
        'example': 'The smartphone market is an oligopoly because a few firms like Apple and Samsung dominate sales.'
    },
    'price discrimination': {
        'definition': 'Price discrimination occurs when a seller charges different prices to different customers for the same good or service.',
        'importance': 'It can increase profits and sometimes lead to more efficient use of capacity, but it can also be unfair.',
        'example': 'Airlines often charge different ticket prices depending on booking time, seat class, and customer segment.'
    },
    'cost structure': {
        'definition': 'Cost structure shows the relative size of fixed and variable costs for a business.',
        'importance': 'Understanding cost structure helps firms decide pricing, output, and when they break even.',
        'example': 'A bakery has fixed rents and equipment costs, plus variable costs for ingredients and labor per loaf baked.'
    },
    'break even analysis': {
        'definition': 'Break-even analysis finds the sales level needed for revenue to equal total costs.',
        'importance': 'It is a key decision tool for new products and for planning profit targets.',
        'example': 'A coffee shop might calculate how many cups it must sell each month to cover rent and wages.'
    },
    'swot analysis': {
        'definition': 'SWOT analysis evaluates strengths, weaknesses, opportunities, and threats for a business or project.',
        'importance': 'It provides a simple framework for strategic planning and self-assessment.',
        'example': 'A startup may use SWOT to decide whether to launch a new service by weighing its strong brand against a crowded market.'
    },
    'market failure': {
        'definition': 'Market failure happens when markets fail to allocate resources efficiently on their own.',
        'importance': 'Recognizing market failures helps justify government intervention in areas like public goods and externalities.',
        'example': 'Pollution is a market failure because firms may not pay for the harm they impose on others.'
    },
    'comparative advantage': {
        'definition': 'Comparative advantage means a country should specialize in producing goods it can make at lower opportunity cost than others.',
        'importance': 'It explains why trade can benefit all countries even when one country is more productive in every good.',
        'example': 'Even if one country makes both cars and textiles more efficiently, it can still benefit by specializing in the good with the lower opportunity cost.'
    },
    'marginal cost': {
        'definition': 'Marginal cost is the additional cost of producing one more unit of output.',
        'importance': 'Firms compare marginal cost to marginal revenue to decide how much to produce.',
        'example': 'If producing one extra shirt costs an additional $5, the firm will only make it if it can sell it for more than $5.'
    },
    'marginal utility': {
        'definition': 'Marginal utility is the extra satisfaction gained from consuming one more unit of a good.',
        'importance': 'It helps explain why demand curves slope downward as additional units become less valuable.',
        'example': 'The first slice of pizza may be very satisfying, but the fourth slice delivers less extra satisfaction than the first.'
    },
    'price ceiling': {
        'definition': 'A price ceiling is a legal maximum price set below the market equilibrium, such as rent control.',
        'importance': 'It can create shortages and reduce the quality of goods or services.',
        'example': 'When rent is capped below market rates, landlords may rent fewer apartments or cut maintenance.'
    },
    'price floor': {
        'definition': 'A price floor is a legal minimum price set above the market equilibrium, like a minimum wage.',
        'importance': 'It can create surpluses or unemployment if the floor is too high.',
        'example': 'A minimum wage above market-clearing levels can increase unemployment among low-skilled workers.'
    },
    'budget deficit': {
        'definition': 'A budget deficit happens when government spending exceeds tax revenue in a year.',
        'importance': 'Persistent deficits increase national debt and can affect interest rates and future spending.',
        'example': 'When a government spends more on infrastructure than it collects in taxes, it runs a budget deficit.'
    },
    'national debt': {
        'definition': 'National debt is the total amount the government owes from past budget deficits.',
        'importance': 'It matters because debt payments can limit future fiscal flexibility and require tax revenue to service it.',
        'example': 'A country with high national debt may need to spend more on interest payments instead of schools or health care.'
    },
    'externalities': {
        'definition': 'Externalities are costs or benefits that affect third parties who are not part of an economic transaction.',
        'importance': 'They are a common reason why markets do not allocate resources efficiently without regulation.',
        'example': 'A factory emitting pollution imposes costs on nearby residents who are not part of the sale of its products.'
    },
    'public goods': {
        'definition': 'Public goods are goods that are non-rival and non-excludable, like national defense or clean air.',
        'importance': 'Because private markets tend to underprovide them, governments often supply public goods.',
        'example': 'A lighthouse is a public good because ships can benefit from its light without reducing others’ access.'
    },
    'trade balance': {
        'definition': 'The trade balance is the difference between a country’s exports and imports of goods and services.',
        'importance': 'A trade deficit or surplus can signal competitiveness and affect exchange rates.',
        'example': 'If a country exports $100 billion and imports $120 billion, it has a $20 billion trade deficit.'
    },
    'exchange rate': {
        'definition': 'An exchange rate is the price of one currency expressed in terms of another.',
        'importance': 'It affects international trade, investment, and the cost of imports and exports.',
        'example': 'If the dollar strengthens, imported goods become cheaper for US consumers but exports become more expensive abroad.'
    },
    'economic growth': {
        'definition': 'Economic growth is the increase in a country’s output of goods and services over time.',
        'importance': 'Sustained growth raises living standards and expands opportunities for employment and investment.',
        'example': 'Rising GDP per year usually means more jobs, higher incomes, and improved public services.'
    },
    'labor market': {
        'definition': 'The labor market describes the supply of workers and demand for workers by firms.',
        'importance': 'It helps explain wage trends, unemployment, and how economic conditions affect jobs.',
        'example': 'When firms expand, demand for labor increases and wages may rise as workers become harder to find.'
    },
    'consumer surplus': {
        'definition': 'Consumer surplus is the difference between what consumers are willing to pay and what they actually pay.',
        'importance': 'It measures the benefit consumers receive from market transactions.',
        'example': 'If a shopper would pay $50 for shoes but buys them for $30, the $20 difference is consumer surplus.'
    },
    'producer surplus': {
        'definition': 'Producer surplus is the difference between the price producers receive and the minimum they would accept.',
        'importance': 'It measures the gain that producers get from selling at market prices.',
        'example': 'If a farmer would sell wheat for at least $5 per bushel but receives $8, the $3 difference is producer surplus.'
    }
}

topic_aliases = {
    'gdp': ['gdp', 'gross domestic product', 'output', 'economic output'],
    'inflation': ['inflation', 'price rise', 'price increase', 'cost of living'],
    'unemployment': ['unemployment', 'jobless', 'unemployed', 'labor market'],
    'monetary policy': ['monetary policy', 'interest rate', 'central bank', 'fed policy'],
    'fiscal policy': ['fiscal policy', 'tax', 'government spending', 'budget policy'],
    'aggregate demand': ['aggregate demand', 'total demand', 'economy-wide demand'],
    'aggregate supply': ['aggregate supply', 'total supply', 'economy-wide supply'],
    'supply and demand': ['supply and demand', 'market equilibrium', 'supply demand'],
    'elasticity': ['elasticity', 'responsive', 'sensitivity', 'price sensitivity'],
    'utility maximization': ['utility maximization', 'satisfaction', 'consumer choice', 'maximize utility'],
    'opportunity cost': ['opportunity cost', 'trade off', 'trade-off', 'alternative cost'],
    'ppf': ['ppf', 'production possibility frontier', 'production frontier'],
    'game theory': ['game theory', 'strategic interaction', 'strategy'],
    'perfect competition': ['perfect competition', 'competitive market'],
    'monopoly': ['monopoly', 'single seller'],
    'oligopoly': ['oligopoly', 'few firms'],
    'price discrimination': ['price discrimination', 'different prices'],
    'cost structure': ['cost structure', 'fixed cost', 'variable cost', 'cost mix'],
    'break even analysis': ['break even analysis', 'break-even', 'break even'],
    'swot analysis': ['swot analysis', 'strengths weaknesses opportunities threats'],
    'market failure': ['market failure', 'inefficient market', 'market inefficiency'],
    'comparative advantage': ['comparative advantage', 'trade advantage'],
    'marginal cost': ['marginal cost', 'additional cost', 'extra cost'],
    'marginal utility': ['marginal utility', 'additional satisfaction', 'extra satisfaction'],
    'price ceiling': ['price ceiling', 'maximum price', 'rent control'],
    'price floor': ['price floor', 'minimum price', 'minimum wage'],
    'budget deficit': ['budget deficit', 'government deficit', 'fiscal deficit'],
    'national debt': ['national debt', 'public debt', 'government debt'],
    'externalities': ['externalities', 'spillover effects', 'external effect'],
    'public goods': ['public goods', 'non-excludable', 'non-rival'],
    'trade balance': ['trade balance', 'balance of trade', 'exports minus imports'],
    'exchange rate': ['exchange rate', 'currency price', 'fx rate'],
    'economic growth': ['economic growth', 'growth rate', 'gdp growth'],
    'labor market': ['labor market', 'job market', 'labor supply'],
    'consumer surplus': ['consumer surplus', 'consumer benefit'],
    'producer surplus': ['producer surplus', 'producer benefit']
}



def normalize_text(user_input):
    tokens = word_tokenize(user_input.lower())
    return [stemmer.stem(token) for token in tokens if token.isalpha() and token not in stop_words]


def build_topic_keyword_sets():
    keyword_sets = {}
    for topic, aliases in topic_aliases.items():
        normalized = set()
        for alias in aliases:
            normalized.update(normalize_text(alias))
        normalized.update(normalize_text(topic))
        keyword_sets[topic] = normalized
    return keyword_sets


topic_keywords = build_topic_keyword_sets()


def find_intent(user_input):
    tokens = normalize_text(user_input)

    best_topic = None
    best_score = 0
    for topic, keywords in topic_keywords.items():
        score = sum(1 for token in tokens if token in keywords)
        if score > best_score:
            best_topic = topic
            best_score = score

    if best_score >= 1:
        return 'topic', best_topic

    if any(token in {'topic', 'topics', 'list', 'learn', 'study', 'available', 'subject', 'subjects'} for token in tokens):
        return 'topic_list', None

    return 'unknown', None


def create_topic_response(topic):
    topic_data = topics.get(topic)
    if not topic_data:
        return 'I am unable to find information for that topic at the moment.'

    definition = topic_data.get('definition', '')
    importance = topic_data.get('importance', '')
    example = topic_data.get('example', '')
    response_parts = [definition]
    if importance:
        response_parts.append(importance)
    if example:
        response_parts.append(example)
    return ' '.join(response_parts)


def create_topic_list_response():
    topic_names = sorted([name.title() for name in topics.keys()])
    return ('You can learn about the following economics topics: ' + ', '.join(topic_names) +
            '. Ask about any of these topics to get a clear explanation.')


def generate_response(user_input):
    normalized = user_input.strip().lower()
    if normalized in {'exit', 'quit'}:
        return 'Goodbye. Keep studying economics.'

    intent, topic = find_intent(user_input)
    if intent == 'topic_list':
        return create_topic_list_response()
    if intent == 'topic':
        return create_topic_response(topic)
    return ('Please ask about a specific economics topic such as GDP, inflation, unemployment, monetary policy, ' 
            'or fiscal policy. You can also ask for a list of topics to learn.')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = generate_response(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)